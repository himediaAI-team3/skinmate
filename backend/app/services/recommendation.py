from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import List
import logging

from app.repository.recommendation import RecommendationRepository
from app.repository.diagnosis import DiagnosisRepository
from app.repository.analysis import AnalysisRepository
from app.repository.cosmetic import CosmeticRepository
from app.services.vector_store import VectorStoreService
from app.utils.prompt import load_prompt
from app.utils.llm import parse_llm_json
from app.core.config.llm import get_llm, TEMPERATURE_RECOMMENDATION_QUERY, TEMPERATURE_RECOMMENDATION_SELECT
from app.core.exception.exceptions import VectorSearchException, LLMParsingException
from fastapi import status as http_status

logger = logging.getLogger(__name__)


# Pydantic 모델: 검색 쿼리
class SearchQuery(BaseModel):
    disease_name: str = Field(description="질환명")
    dense_query: str = Field(description="Dense 검색용 자연어 쿼리")
    sparse_keywords: str = Field(description="Sparse 검색용 키워드")


# Pydantic 모델: 추천 결과
class RecommendationItem(BaseModel):
    ranking: int = Field(description="추천 순위")
    cosmetic_id: int = Field(description="화장품 ID")
    reason: str = Field(description="추천 이유")


class RecommendationResult(BaseModel):
    recommendations: List[RecommendationItem] = Field(description="추천 화장품 목록")


class RecommendationService:
    
    @staticmethod
    def create_recommendations(db: Session, analysis_id: int) -> List:
        """
        RAG 파이프라인을 통한 화장품 추천 생성
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            
        Returns:
            Recommendation 리스트
        """
        logger.info(f"==== RAG 파이프라인 시작 (analysis_id: {analysis_id}) ====")
        
        # 1. 진단 결과 조회
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
        if not diagnosis:
            raise ValueError(f"진단 결과를 찾을 수 없습니다: analysis_id={analysis_id}")
        
        disease_name = diagnosis.disease_name
        summary = diagnosis.summary
        logger.info(f"진단 결과: {disease_name}")
        logger.info(f"진단 요약: {summary[:100]}...")
        
        # 2. 분석 정보 조회 (피부타입, 가격대)
        analysis = AnalysisRepository.get_by_id(db, analysis_id)
        if not analysis:
            raise ValueError(f"분석 정보를 찾을 수 없습니다: analysis_id={analysis_id}")
        
        skin_type = analysis.skin_type
        min_price = analysis.min_price or 0
        max_price = analysis.max_price or 999999
        logger.info(f"분석 정보: skin_type={skin_type}, price_range={min_price}~{max_price}")
        
        # 3. 검색 쿼리 생성
        query_data = RecommendationService._build_search_query_from_diagnosis(db, analysis_id)
        
        # 4. 하이브리드 검색 (Qdrant)
        logger.info("Qdrant 하이브리드 검색 시작...")
        search_results = VectorStoreService.search_hybrid(
            query_dense_text=query_data["dense_query"],
            query_sparse_text=query_data["sparse_keywords"],
            min_price=min_price,
            max_price=max_price,
            skin_type=skin_type,
            disease_name=query_data.get("disease_name"),
            limit=10
        )
        
        if len(search_results) == 0:
            logger.warning(
                f"벡터 DB 검색 결과 없음: disease={disease_name}, "
                f"price={min_price}~{max_price}, skin_type={skin_type}"
            )
            raise VectorSearchException(
                http_status.HTTP_404_NOT_FOUND,
                f"벡터 DB에서 '{disease_name}' 질환에 적합한 화장품을 찾을 수 없습니다. "
                f"필터 조건: 가격대({min_price:,}~{max_price:,}원), 피부타입({skin_type or '미지정'})"
            )
        
        logger.info(f"Vector 검색 결과 Top {len(search_results)}:")
        for i, result in enumerate(search_results, 1):
            logger.info(f"  {i}. cosmetic_id={result['cosmetic_id']} (유사도: {result['score']:.4f})")
        
        # 5. MySQL에서 상세 정보 조회
        cosmetic_ids = [r['cosmetic_id'] for r in search_results]
        cosmetics = CosmeticRepository.get_by_ids(db, cosmetic_ids)
        
        # 6. LLM에게 Top 10 전달하여 최종 3개 선정
        logger.info("LLM에게 Top 10 전달...")
        final_recommendations = RecommendationService._select_top3_with_llm(
            diagnosis=diagnosis,
            cosmetics=cosmetics,
            search_scores={r['cosmetic_id']: r['score'] for r in search_results},
            analysis=analysis
        )
        
        # 7. 결과 처리
        if len(final_recommendations) == 0:
            logger.warning("LLM이 적합한 제품이 없다고 판단했습니다.")
            logger.info(f"========== RAG 파이프라인 완료 (추천 제품 0개) ==========")
            return []
        
        logger.info(f"LLM 최종 선정 완료 ({len(final_recommendations)}개):")
        for rec in final_recommendations:
            logger.info(f"  {rec['ranking']}. cosmetic_id={rec['cosmetic_id']} - {rec['reason'][:50]}...")
        
        # 8. MySQL recommendation 테이블 저장
        recommendations_data = [
            {
                "analysis_id": analysis_id,
                "cosmetic_id": rec["cosmetic_id"],
                "ranking": rec["ranking"],
                "reason": rec["reason"]
            }
            for rec in final_recommendations
        ]
        
        saved_recommendations = RecommendationRepository.create_bulk(db, recommendations_data)
        logger.info(f"MySQL 저장 완료: recommendation_id {[r.recommendation_id for r in saved_recommendations]}")
        logger.info(f"========== RAG 파이프라인 완료 ==========")
        
        return saved_recommendations
    
    @staticmethod
    def _build_search_query_from_diagnosis(db: Session, analysis_id: int) -> dict:
        """진단 결과를 검색 쿼리로 변환 (LLM 호출 + Structured Output)"""
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
        if not diagnosis:
            raise ValueError(f"진단 결과를 찾을 수 없습니다: analysis_id={analysis_id}")
        
        # 분석 정보 조회 (피부타입)
        analysis = AnalysisRepository.get_by_id(db, analysis_id)
        skin_type = analysis.skin_type if analysis and analysis.skin_type else "알 수 없음"
        
        # 프롬프트 로드
        instruction = load_prompt("summary_refine.yaml")
        filled = instruction.format(
            disease_name=diagnosis.disease_name,
            summary=diagnosis.summary,
            skin_type=skin_type
        )
        
        # Structured Output을 지원하는 LLM 생성
        llm = get_llm(TEMPERATURE_RECOMMENDATION_QUERY)
        structured_llm = llm.with_structured_output(SearchQuery)
        
        try:
            # Structured Output 직접 호출
            result = structured_llm.invoke([HumanMessage(content=filled)])
            
            logger.info(f"검색 쿼리 생성 완료: dense={result.dense_query[:50]}...")
            logger.info(f"검색 쿼리 sparse={result.sparse_keywords[:80] if len(result.sparse_keywords) > 80 else result.sparse_keywords}")
            
            return {
                "disease_name": result.disease_name,
                "dense_query": result.dense_query,
                "sparse_keywords": result.sparse_keywords,
            }
        except Exception as e:
            logger.error(f"검색 쿼리 생성 실패: {e}")
            # 폴백: 기존 방식 시도
            resp = llm.invoke([HumanMessage(content=filled)])
            data = parse_llm_json(resp.content)
            return {
                "disease_name": data["disease_name"],
                "dense_query": data["dense_query"],
                "sparse_keywords": data["sparse_keywords"],
            }
    
    @staticmethod
    def _select_top3_with_llm(diagnosis, cosmetics: List, search_scores: dict, analysis) -> List[dict]:
        """
        LLM을 사용하여 Top 10 중 최종 3개 선정
        
        Args:
            diagnosis: 진단 정보
            cosmetics: 화장품 리스트 (Top 10)
            search_scores: {cosmetic_id: score} 유사도 점수
            analysis: 분석 정보 (피부타입, 가격대)
            
        Returns:
            List[dict]: [{"ranking": 1, "cosmetic_id": 1, "reason": "..."}]
        """
        # LLM 초기화
        llm = get_llm(TEMPERATURE_RECOMMENDATION_SELECT)
        
        # 프롬프트 로드
        instruction = load_prompt("recommendation.yaml")
        
        # 화장품 정보 포맷팅
        cosmetics_info = []
        for cosmetic in cosmetics:
            cosmetics_info.append({
                "cosmetic_id": cosmetic.cosmetic_id,
                "name": cosmetic.name,
                "brand": cosmetic.brand,
                "category": cosmetic.category,
                "price": int(cosmetic.price) if cosmetic.price else 0,
                "skin_type": cosmetic.skin_type,
                "skin_disease": cosmetic.skin_disease,
                "main_effect": cosmetic.main_effect,
                "care_symptom": cosmetic.care_symptom,
                "key_ingredient": cosmetic.key_ingredient,
                "short_description": cosmetic.short_description,
                "similarity_score": round(search_scores.get(cosmetic.cosmetic_id, 0), 4)
            })
        
        # 사용자 정보 포맷팅
        user_info = []
        if analysis.skin_type:
            user_info.append(f"- 피부타입: {analysis.skin_type}")
        
        user_info_text = "\n".join(user_info) if user_info else "- 정보 없음"
        
        # 화장품 정보를 문자열로 변환
        import json
        cosmetics_json = json.dumps(cosmetics_info, ensure_ascii=False, indent=2)
        
        # 사용자 입력 구성
        user_input = f"""
**사용자 정보:**
{user_info_text}

**사용자 피부 진단:**
- 질환: {diagnosis.disease_name}
- 증상: {diagnosis.summary}

**추천 후보 화장품 (Top 10):**
{cosmetics_json}

위 10개 중 사용자에게 가장 적합한 3개를 선정하고 각각의 추천 이유를 작성하세요.
"""
        
        # Structured Output을 지원하는 LLM 생성
        structured_llm = llm.with_structured_output(RecommendationResult)
        
        # 최종 프롬프트 구성
        final_prompt = f"{instruction}\n\n{user_input}"
        
        # LLM 호출 및 Structured Output 파싱
        try:
            result = structured_llm.invoke([HumanMessage(content=final_prompt)])
            recommendations = result.recommendations
            
            # Pydantic 모델 → dict 변환
            recommendations_dict = [
                {
                    "ranking": rec.ranking,
                    "cosmetic_id": rec.cosmetic_id,
                    "reason": rec.reason
                }
                for rec in recommendations
            ]
            
            # 유연한 검증: 0~3개 모두 허용
            if len(recommendations_dict) == 0:
                logger.warning(f"LLM이 적합한 제품이 없다고 판단했습니다.")
            elif len(recommendations_dict) > 3:
                logger.warning(f"LLM이 {len(recommendations_dict)}개 반환. 상위 3개만 사용합니다.")
                recommendations_dict = recommendations_dict[:3]
            else:
                logger.info(f"LLM이 {len(recommendations_dict)}개 제품을 선정했습니다.")
            
            return recommendations_dict
            
        except Exception as e:
            logger.error(f"LLM 응답 파싱 실패 (Structured Output): {e}")
            
            # 폴백: 기존 방식 시도
            try:
                logger.info("폴백: 기존 JSON 파싱 방식 시도")
                response = llm.invoke([HumanMessage(content=final_prompt)])
                result = parse_llm_json(response.content)
                recommendations = result.get("recommendations", [])
                
                if len(recommendations) > 3:
                    recommendations = recommendations[:3]
                
                return recommendations
                
            except Exception as fallback_error:
                logger.error(f"폴백도 실패: {fallback_error}")
                logger.error(f"LLM 응답 원문: {response.content if 'response' in locals() else 'N/A'}")
                
                raise LLMParsingException(
                    http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"LLM이 올바른 JSON 형식을 반환하지 않았습니다. Vector 검색은 {len(cosmetics)}개 성공."
                )
