from sqlalchemy.orm import Session
from app.repository.recommendation import RecommendationRepository
from typing import List


class RecommendationService:
    
    @staticmethod
    def create_recommendations(db: Session, analysis_id: int, member_id: int) -> List:
        """
        화장품 추천 생성 (현재: 더미 데이터, 나중: RAG)
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            member_id: 회원 ID (개인화용)
            
        Returns:
            Recommendation 리스트
        """
        # 더미 추천 데이터 (cosmetic_id: 1, 2, 3 가정)
        recommendations_data = [
            {
                "analysis_id": analysis_id,
                "cosmetic_id": 1,
                "ranking": 1,
                "reason": "여드름 진정에 효과적"
            },
            {
                "analysis_id": analysis_id,
                "cosmetic_id": 2,
                "ranking": 2,
                "reason": "모공 케어에 적합"
            },
            {
                "analysis_id": analysis_id,
                "cosmetic_id": 3,
                "ranking": 3,
                "reason": "수분 공급 우수"
            }
        ]
        
        return RecommendationRepository.create_bulk(db, recommendations_data)


    @staticmethod
    def create_rag_recommendations(db: Session, analysis_id: int) -> List:
        """
        RAG 파이프라인을 사용해 Top3 화장품을 검색하여 DB에 저장한다.
        - Diagnosis(질병명+summary)를 LLM으로 검색 질의로 변환
        - Dense/Sparse 하이브리드 검색(RRF)
        - 상위 3개를 ranking 1..3으로 저장
        실패 시 기존 더미 전략으로 폴백
        """
        try:
            from app.repository.diagnosis import DiagnosisRepository
            from app.repository.analysis import AnalysisRepository
            from app.core.config.embedding import embedding_model
            from app.core.config.qdrant import qdrant_client, QdrantConfig
            from app.rag.query_generator import generate_query_from_diagnosis
            from app.rag.vocabulary import load_vocabulary
            from app.rag.vector_builder import create_search_sparse_vector
            from app.services.member import MemberService
            from qdrant_client.models import Filter, FieldCondition, Range, NamedVector, NamedSparseVector

            # 1) 최신 진단 로드
            diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
            if not diagnosis:
                raise RuntimeError("진단 결과가 존재하지 않습니다")

            disease_name = getattr(diagnosis, "disease_name", "") or ""
            summary = getattr(diagnosis, "summary", "") or ""

            # 1-1) 사용자 정보 로드 (skin_type, price range)
            analysis = AnalysisRepository.get_by_id(db, analysis_id)
            member = None
            user_skin_type = None
            min_price = None
            max_price = None
            if analysis and getattr(analysis, "member_id", None):
                member = MemberService.get_member(db, analysis.member_id)
                if member:
                    user_skin_type = getattr(member, "skin_type", None)
                    min_price = getattr(member, "min_price", None)
                    max_price = getattr(member, "max_price", None)
                    print(f"[DEBUG] 사용자 정보: skin_type={user_skin_type}, min_price={min_price}, max_price={max_price}")
                else:
                    print(f"[DEBUG] Member 조회 실패: member_id={analysis.member_id}")
            else:
                print(f"[DEBUG] Analysis 또는 member_id 없음: analysis={analysis is not None}, member_id={getattr(analysis, 'member_id', None) if analysis else None}")

            # 2) LLM으로 검색 쿼리 생성
            print(f"[DEBUG] LLM 쿼리 생성 시작: disease={disease_name}, summary={summary[:50]}...")
            query_spec = generate_query_from_diagnosis(disease_name, summary)
            dense_text = query_spec.get("dense_text", "")
            keywords = query_spec.get("keywords", [])
            print(f"[DEBUG] LLM 쿼리 생성 완료: dense_text 길이={len(dense_text)}, keywords={keywords[:5]}...")

            # 3) Vocabulary 로드 및 벡터 생성
            vocabulary = load_vocabulary()
            dense_vector = embedding_model.encode(dense_text).tolist() if dense_text else []
            sparse_vector = create_search_sparse_vector(keywords, vocabulary)

            # 4) 가격 하드 필터(must Range)만 적용
            must_conditions = []
            if min_price is not None or max_price is not None:
                price_range_kwargs = {}
                if min_price is not None:
                    price_range_kwargs["gte"] = float(min_price)
                if max_price is not None:
                    price_range_kwargs["lte"] = float(max_price)
                must_conditions.append(
                    FieldCondition(key="price", range=Range(**price_range_kwargs))
                )
            query_filter = Filter(must=must_conditions) if must_conditions else None
            
            # 디버깅: 필터 정보 출력
            print(f"[DEBUG] 가격 필터: min={min_price}, max={max_price}, filter={query_filter is not None}")

            # 5) 검색 실행 (상위 10 → Top3 사용)
            # 최신 qdrant-client에서는 각각 검색 후 RRF로 수동 결합
            res_dense = qdrant_client.search(
                collection_name=QdrantConfig.COLLECTION_NAME,
                query_vector=NamedVector(name="dense", vector=dense_vector),
                limit=20,
                with_payload=True,
                query_filter=query_filter,
            )
            res_sparse = qdrant_client.search(
                collection_name=QdrantConfig.COLLECTION_NAME,
                query_vector=NamedSparseVector(name="sparse", vector=sparse_vector),
                limit=20,
                with_payload=True,
                query_filter=query_filter,
            )
            
            # 디버깅: 검색 결과 수 출력
            print(f"[DEBUG] 검색 결과: dense={len(res_dense)}, sparse={len(res_sparse)}")

            from collections import defaultdict
            scores = defaultdict(float)

            def add_rrf(results, weight: float = 1.0):
                for idx, point in enumerate(results, start=1):
                    scores[point.id] += weight * (1.0 / (60 + idx))

            # 가중치: sparse를 약간 강화
            add_rrf(res_dense, weight=1.0)
            add_rrf(res_sparse, weight=1.2)

            payload_map = {}
            for p in list(res_dense) + list(res_sparse):
                payload_map[p.id] = p.payload or {}

            # 소프트 부스팅: 질환 동의어 / 피부타입 호환성
            disease_synonyms = {
                "아토피": {"아토피", "아토피 피부염", "Atopic dermatitis"},
                "여드름": {"여드름", "acne"},
                "주사": {"주사", "rosacea"},
                "지루": {"지루", "지루피부염", "seborrheic dermatitis"},
                "건선": {"건선", "psoriasis"},
                "정상": {"정상"},
            }
            disease_set = disease_synonyms.get(disease_name, {disease_name} if disease_name else set())

            compatible_skin_types = {
                "건성": {"건성", "중건성", "민감성"},
                "지성": {"지성", "복합성", "민감성"},
                "복합성": {"복합성", "지성", "건성"},
                "민감성": {"민감성", "건성", "복합성"},
            }

            for pid, base in list(scores.items()):
                payload = payload_map.get(pid, {})
                # 질환 소프트 부스트
                if disease_set and (payload.get("skin_disease") in disease_set):
                    scores[pid] = base + 0.1
                # 피부타입 소프트 부스트
                if user_skin_type:
                    p_skin = payload.get("skin_type")
                    if p_skin and p_skin == user_skin_type:
                        scores[pid] = scores[pid] + 0.1
                    elif p_skin and user_skin_type in compatible_skin_types and p_skin in compatible_skin_types[user_skin_type]:
                        scores[pid] = scores[pid] + 0.05

            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print(f"[DEBUG] RRF 점수 계산 완료: 총 {len(scores)}개 항목")
            top_ids = [pid for pid, _ in ranked[:3]]
            top_points = [type("_Point", (), {"payload": payload_map.get(pid, {})}) for pid in top_ids]
            print(f"[DEBUG] Top3 ID: {top_ids}")
            if not top_points:
                raise RuntimeError(f"검색 결과가 비어 있습니다. scores 개수: {len(scores)}, ranked 개수: {len(ranked)}")

            # 6) Recommendation 저장 데이터 구성
            recommendations_data: List[dict] = []
            for rank, point in enumerate(top_points, start=1):
                payload = getattr(point, "payload", {}) or {}
                cosmetic_id = payload.get("cosmetic_id")
                reason = f"{disease_name}에 적합: {payload.get('main_effect') or '주요 효능 매칭'}"
                recommendations_data.append({
                    "analysis_id": analysis_id,
                    "cosmetic_id": int(cosmetic_id) if cosmetic_id is not None else 0,
                    "ranking": rank,
                    "reason": reason,
                })

            # 기존 추천 삭제 후 저장(중복 방지)
            try:
                from app.repository.recommendation import RecommendationRepository as RR
                RR.delete_by_analysis_id(db, analysis_id)
                db.commit()
            except Exception:
                pass

            return RecommendationRepository.create_bulk(db, recommendations_data)

        except Exception as e:
            # 폴백: 기존 더미 3개
            import traceback
            print("=" * 60)
            print(f"[ERROR] RAG 추천 실패 - 예외 타입: {type(e).__name__}")
            print(f"[ERROR] 예외 메시지: {str(e)}")
            print("=" * 60)
            traceback.print_exc()
            print("=" * 60)
            recommendations_data = [
                {"analysis_id": analysis_id, "cosmetic_id": 1, "ranking": 1, "reason": "기본 추천"},
                {"analysis_id": analysis_id, "cosmetic_id": 2, "ranking": 2, "reason": "기본 추천"},
                {"analysis_id": analysis_id, "cosmetic_id": 3, "ranking": 3, "reason": "기본 추천"},
            ]
            return RecommendationRepository.create_bulk(db, recommendations_data)