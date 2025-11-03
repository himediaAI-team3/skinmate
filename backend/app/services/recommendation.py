"""추천 서비스 (Baseline 버전 - must_keywords/avoid 주석 처리 가능)"""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.repository.recommendation import RecommendationRepository
from typing import List
from app.rag.vocabulary import load_vocabulary


from app.repository.diagnosis import DiagnosisRepository
from app.repository.analysis import AnalysisRepository
from app.core.config.embedding import embedding_model
from app.core.config.qdrant import qdrant_client, QdrantConfig
from app.rag.query_generator import generate_query_from_diagnosis, generate_product_reason
from app.rag.vocabulary import load_vocabulary
from qdrant_client.models import Filter, FieldCondition, Range, NamedVector, NamedSparseVector, SparseVector

# IDF 캐시 (전역)
_IDF_CACHE = None


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
        recommendations_data = [
            {"analysis_id": analysis_id, "cosmetic_id": 1, "ranking": 1, "reason": "여드름 진정에 효과적"},
            {"analysis_id": analysis_id, "cosmetic_id": 2, "ranking": 2, "reason": "모공 케어에 적합"},
            {"analysis_id": analysis_id, "cosmetic_id": 3, "ranking": 3, "reason": "수분 공급 우수"}
        ]
        return RecommendationRepository.create_bulk(db, recommendations_data)


    @staticmethod
    def load_idf():
        """IDF 사전 로드 (캐싱)"""
        global _IDF_CACHE
        if _IDF_CACHE is not None:
            return _IDF_CACHE
        
        project_root = Path(__file__).parent.parent.parent
        idf_path = project_root / "data" / "bm25_idf.json"
        
        if not idf_path.exists():
            _IDF_CACHE = {}
            return _IDF_CACHE
        
        with idf_path.open("r", encoding="utf-8") as f:
            _IDF_CACHE = json.load(f)
        return _IDF_CACHE



    @staticmethod
    def create_rag_recommendations(db: Session, analysis_id: int) -> List:
        """
        RAG 파이프라인 (Baseline 버전)
        
        설정:
        - USE_MUST_KEYWORDS_WEIGHT: must_keywords 가중치 사용 여부
        - USE_AVOID_PENALTY: avoid_ingredients 페널티 사용 여부
        """
        # ===== 실험 설정 =====
        USE_MUST_KEYWORDS_WEIGHT = False  # True로 바꾸면 must_keywords 가중치 2.0 적용
        USE_AVOID_PENALTY = False         # True로 바꾸면 avoid_ingredients 페널티 -0.15 적용
        # ====================
        
        try:
            

            # 1) 진단 로드
            diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
            if not diagnosis:
                raise RuntimeError("진단 결과가 존재하지 않습니다")

            disease_name = getattr(diagnosis, "disease_name", "") or ""
            summary = getattr(diagnosis, "summary", "") or ""

            # 1-1) 사용자 정보 로드
            analysis = AnalysisRepository.get_by_id(db, analysis_id)
            user_info = {}
            
            if analysis:
                # 모든 사용자 정보는 analysis에서만 가져오기 (없으면 None)
                user_info['skin_type'] = getattr(analysis, "skin_type", None)
                min_price = getattr(analysis, "min_price", None)
                max_price = getattr(analysis, "max_price", None)
                user_info['min_price'] = min_price
                user_info['max_price'] = max_price
                print(f"[DEBUG] 사용자 정보: {user_info}")
            else:
                min_price = None
                max_price = None

            # 2) LLM 쿼리 생성
            print(f"[DEBUG] LLM 쿼리 생성: disease={disease_name}")
            query_spec = generate_query_from_diagnosis(disease_name, summary, user_info)
            dense_text = query_spec.get("dense_text", "")
            keywords = query_spec.get("keywords", [])
            must_keywords = query_spec.get("must_keywords", [])
            avoid_ingredients = query_spec.get("avoid_ingredients", [])
            consulting_notes = query_spec.get("notes", "")
            
            print(f"[DEBUG] keywords={keywords[:5]}, must={must_keywords}")

            # 3) 벡터 생성
            vocabulary = load_vocabulary()
            idf = RecommendationService.load_idf()  # ⭐ IDF 로드
            dense_vector = embedding_model.encode(dense_text).tolist() if dense_text else []
            
            # ⭐ BM25 Sparse 벡터 생성
            from app.rag.vector_builder import create_search_bm25_sparse_vector
            sparse_vector = create_search_bm25_sparse_vector(keywords, vocabulary, idf)
            # Sparse 벡터 생성
            sparse_indices = []
            sparse_values = []
            
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword in vocabulary:
                    idx = vocabulary[keyword]
                    
                    # ===== must_keywords 가중치 적용 =====
                    if USE_MUST_KEYWORDS_WEIGHT:
                        weight = 2.0 if keyword in must_keywords else 1.0
                        print(f"[DEBUG] '{keyword}' 가중치: {weight}")
                    else:
                        weight = 1.0  # Baseline: 모두 동일
                    # ====================================
                    
                    sparse_indices.append(idx)
                    sparse_values.append(weight)
            
            sparse_vector = SparseVector(indices=sparse_indices, values=sparse_values)
            print(f"[DEBUG] Sparse 벡터: {len(sparse_indices)}개 키워드")

            # 4) 가격 필터
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

            # 5) 검색
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
            
            print(f"[DEBUG] 검색: dense={len(res_dense)}, sparse={len(res_sparse)}")

            # 6) RRF
            from collections import defaultdict
            scores = defaultdict(float)

            def add_rrf(results, weight: float = 1.0):
                for idx, point in enumerate(results, start=1):
                    scores[point.id] += weight * (1.0 / (60 + idx))

            add_rrf(res_dense, weight=1.0)
            add_rrf(res_sparse, weight=1.3)

            payload_map = {}
            for p in list(res_dense) + list(res_sparse):
                payload_map[p.id] = p.payload or {}

            # 7) 소프트 부스팅
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
            
            user_skin_type = user_info.get('skin_type')

            for pid, base in list(scores.items()):
                payload = payload_map.get(pid, {})
                
                # 질환 부스트
                if disease_set and (payload.get("skin_disease") in disease_set):
                    scores[pid] = base + 0.1
                
                # 피부타입 부스트
                if user_skin_type:
                    p_skin = payload.get("skin_type")
                    if p_skin and p_skin == user_skin_type:
                        scores[pid] = scores[pid] + 0.1
                    elif p_skin and user_skin_type in compatible_skin_types and p_skin in compatible_skin_types.get(user_skin_type, set()):
                        scores[pid] = scores[pid] + 0.05
                
                # ===== avoid_ingredients 페널티 =====
                if USE_AVOID_PENALTY:
                    description = (payload.get("description") or "").lower()
                    for avoid in avoid_ingredients:
                        if avoid and avoid.lower() in description:
                            scores[pid] = scores[pid] - 0.15
                            print(f"[DEBUG] 제품 {pid} 회피 성분 '{avoid}' 감지 → -0.15점")
                            break
                # ===================================

            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print(f"[DEBUG] 점수 계산 완료: {len(scores)}개")
            
            top_ids = [pid for pid, _ in ranked[:3]]
            top_points = [type("_Point", (), {"payload": payload_map.get(pid, {})}) for pid in top_ids]
            print(f"[DEBUG] Top3 ID: {top_ids}")
            
            if not top_points:
                raise RuntimeError(f"검색 결과 없음")

            # 8) Recommendation 저장
            recommendations_data: List[dict] = []
            for rank, point in enumerate(top_points, start=1):
                payload = getattr(point, "payload", {}) or {}
                cosmetic_id = payload.get("cosmetic_id")
                
                # reason: 모든 순위에서 제품 중심 LLM 생성
                product_info = {
                    'brand': payload.get('brand', ''),
                    'name': payload.get('name', ''),
                    'main_effect': payload.get('main_effect', ''),
                    'key_ingredient': payload.get('key_ingredient', ''),
                    'description': payload.get('description', ''),
                    'care_symptom': payload.get('care_symptom', ''),
                    'price': payload.get('price', 0),
                    'category': payload.get('category', '')
                }
                reason = generate_product_reason(disease_name, product_info, rank, user_info)
                
                recommendations_data.append({
                    "analysis_id": analysis_id,
                    "cosmetic_id": int(cosmetic_id) if cosmetic_id is not None else 0,
                    "ranking": rank,
                    "reason": reason,
                })

            # 기존 추천 삭제
            try:
                from app.repository.recommendation import RecommendationRepository as RR
                RR.delete_by_analysis_id(db, analysis_id)
                db.commit()
            except Exception:
                pass

            print(f"[DEBUG] Top 1 reason: {recommendations_data[0]['reason'][:80]}...")
            print(f"[INFO] must_keywords 가중치: {USE_MUST_KEYWORDS_WEIGHT}, avoid 페널티: {USE_AVOID_PENALTY}")
            
            return RecommendationRepository.create_bulk(db, recommendations_data)

        except Exception as e:
            import traceback
            print("=" * 60)
            print(f"[ERROR] RAG 추천 실패: {type(e).__name__}: {e}")
            traceback.print_exc()
            print("=" * 60)
            
            recommendations_data = [
                {"analysis_id": analysis_id, "cosmetic_id": 1, "ranking": 1, "reason": "기본 추천"},
                {"analysis_id": analysis_id, "cosmetic_id": 2, "ranking": 2, "reason": "기본 추천"},
                {"analysis_id": analysis_id, "cosmetic_id": 3, "ranking": 3, "reason": "기본 추천"},
            ]
            return RecommendationRepository.create_bulk(db, recommendations_data)