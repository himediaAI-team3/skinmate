from sqlalchemy.orm import Session
from app.repository.recommendation import RecommendationRepository
from typing import List

from app.rag.pipeline import recommend_products
from app.schemas.rag import RecommendationItem

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
        
        # 트랜잭션: 생성 후 커밋 및 리프레시
        try:
            recommendations = RecommendationRepository.create_bulk(db, recommendations_data)
            db.commit()
            for rec in recommendations:
                db.refresh(rec)
            return recommendations
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def create_rag_recommendations(db: Session, analysis_id: int) -> List:
        """
        RAG 파이프라인으로 추천 생성 및 DB 저장

        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID

        Returns:
            Recommendation 리스트
        """
        # 기존 추천 삭제 (같은 analysis_id)
        RecommendationRepository.delete_by_analysis_id(db, analysis_id)

        # 파이프라인 실행
        recommendations_data = recommend_products(db, analysis_id)

        # DB 저장 (Service에서 커밋)
        payload = [
            {"analysis_id": analysis_id, **rec.model_dump()} if isinstance(rec, RecommendationItem)
            else {"analysis_id": analysis_id, **RecommendationItem.model_validate(rec).model_dump()}
            for rec in recommendations_data
        ]
        try:
            recommendations = RecommendationRepository.create_bulk(db, payload)
            db.commit()
            for rec in recommendations:
                db.refresh(rec)
            return recommendations
        except Exception:
            db.rollback()
            raise

