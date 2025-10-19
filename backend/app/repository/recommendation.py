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
    

