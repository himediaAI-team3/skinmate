from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation
from typing import List


class RecommendationRepository:
    
    @staticmethod
    def create_bulk(db: Session, recommendations_data: List[dict]) -> List[Recommendation]:
        """추천 정보 여러 개 저장 (TOP 3용)"""
        recommendations = [Recommendation(**data) for data in recommendations_data]
        db.add_all(recommendations)
        db.commit()
        for rec in recommendations:
            db.refresh(rec)
        return recommendations
    
    @staticmethod
    def get_by_analysis_id(db: Session, analysis_id: int) -> List[Recommendation]:
        """분석 ID로 추천 목록 조회 (ranking 순)"""
        return db.query(Recommendation)\
            .filter(Recommendation.analysis_id == analysis_id)\
            .order_by(Recommendation.ranking)\
            .all()
    
    @staticmethod
    def delete_by_analysis_id(db: Session, analysis_id: int) -> int:
        """분석 ID로 추천 정보 삭제"""
        deleted = db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).delete()
        return deleted

