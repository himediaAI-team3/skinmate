from sqlalchemy.orm import Session
from app.models.skin_analysis import SkinAnalysis


class AnalysisRepository:
    
    @staticmethod
    def create(db: Session, analysis_data: dict) -> SkinAnalysis:
        """피부 분석 생성"""
        analysis = SkinAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    

