import json
import os
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.repository.recommendation import RecommendationRepository
from app.repository.diagnosis import DiagnosisRepository
from app.repository.member import MemberRepository
from app.repository.cosmetic import CosmeticRepository
from app.services.vector_store import VectorStoreService
from app.utils.prompt import load_prompt
from typing import List
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    
    @staticmethod
    def create_recommendations(db: Session, analysis_id: int, member_id: int) -> List:
        """
        RAG 파이프라인을 통한 화장품 추천 생성
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            member_id: 회원 ID (개인화용)
            
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
        
        # 2. 회원 정보 조회 (개인화 필터링)
        member = MemberRepository.get_by_id(db, member_id)
        if not member:
            raise ValueError(f"회원 정보를 찾을 수 없습니다: member_id={member_id}")
        
        skin_type = member.skin_type
        min_price = member.min_price or 0
        max_price = member.max_price or 999999
        logger.info(f"회원 정보: skin_type={skin_type}, price_range={min_price}~{max_price}")
        
        # 3. 하이브리드 검색 (Qdrant)
        logger.info("Qdrant 하이브리드 검색 시작...")
        search_results = VectorStoreService.search_by_analysis(
            db=db,
            analysis_id=analysis_id,
            member_id=member_id,
            limit=10
        )
        
        if len(search_results) == 0:
            logger.error(f"Vector 검색 결과가 없습니다. 질환: {disease_name}, 가격대: {min_price}~{max_price}원")
            raise ValueError(
                f"'{disease_name}' 질환에 적합한 화장품을 찾을 수 없습니다. "
                f"가격대({min_price}~{max_price}원)와 필터 조건을 확인하세요."
            )
        
        logger.info(f"Vector 검색 결과 Top {len(search_results)}:")
        for i, result in enumerate(search_results, 1):
            logger.info(f"  {i}. {result['name']} ({result['brand']}) - {result['price']}원 (유사도: {result['score']:.4f})")
        
        # 4. MySQL에서 상세 정보 조회
        cosmetic_ids = [r['cosmetic_id'] for r in search_results]
        cosmetics = CosmeticRepository.get_by_ids(db, cosmetic_ids)
        
        # 5. LLM에게 Top 10 전달하여 최종 3개 선정
        logger.info("LLM에게 Top 10 전달...")
        final_recommendations = RecommendationService._select_top3_with_llm(
            diagnosis=diagnosis,
            cosmetics=cosmetics,
            search_scores={r['cosmetic_id']: r['score'] for r in search_results}
        )
        
        logger.info("LLM 최종 선정 완료:")
        for rec in final_recommendations:
            logger.info(f"  {rec['ranking']}. cosmetic_id={rec['cosmetic_id']} - {rec['reason'][:50]}...")
        
        # 6. MySQL recommendation 테이블 저장
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
    def _select_top3_with_llm(diagnosis, cosmetics: List, search_scores: dict) -> List[dict]:
        """
        LLM을 사용하여 Top 10 중 최종 3개 선정
        
        Args:
            diagnosis: 진단 정보
            cosmetics: 화장품 리스트 (Top 10)
            search_scores: {cosmetic_id: score} 유사도 점수
            
        Returns:
            List[dict]: [{"ranking": 1, "cosmetic_id": 1, "reason": "..."}]
        """
        # LLM 초기화
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
        )
        
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
        
        # 사용자 입력 구성
        user_input = f"""
**사용자 피부 진단:**
- 질환: {diagnosis.disease_name}
- 증상: {diagnosis.summary}

**추천 후보 화장품 (Top 10):**
{json.dumps(cosmetics_info, ensure_ascii=False, indent=2)}

위 10개 중 가장 적합한 3개를 선정하고 각각의 추천 이유를 작성하세요.
"""
        
        # LLM 호출
        messages = [
            HumanMessage(content=f"{instruction}\n\n{user_input}")
        ]
        
        response = llm.invoke(messages)
        
        # JSON 파싱
        try:
            # 응답에서 JSON 추출 (```json ... ``` 제거)
            response_text = response.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            recommendations = result.get("recommendations", [])
            
            # 검증
            if len(recommendations) != 3:
                raise ValueError(f"LLM이 3개가 아닌 {len(recommendations)}개를 반환했습니다.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"LLM 응답 파싱 실패: {e}")
            logger.error(f"LLM 응답 원문: {response.content}")
            
            # 실패 시 상위 3개 반환 (fallback)
            return [
                {
                    "ranking": i + 1,
                    "cosmetic_id": cosmetic.cosmetic_id,
                    "reason": f"{cosmetic.main_effect} 효과로 {diagnosis.disease_name} 케어에 적합합니다."
                }
                for i, cosmetic in enumerate(cosmetics[:3])
            ]
    
        # ==================== 기존 하드코딩 방식 (제거됨) ====================
        # recommendations_data = [
        #     {"analysis_id": analysis_id, "cosmetic_id": 1, "ranking": 1, "reason": "여드름 진정에 효과적"},
        #     {"analysis_id": analysis_id, "cosmetic_id": 2, "ranking": 2, "reason": "모공 케어에 적합"},
        #     {"analysis_id": analysis_id, "cosmetic_id": 3, "ranking": 3, "reason": "수분 공급 우수"}
        # ]
        # return RecommendationRepository.create_bulk(db, recommendations_data)
        # ====================================================================
