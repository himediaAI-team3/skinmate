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

