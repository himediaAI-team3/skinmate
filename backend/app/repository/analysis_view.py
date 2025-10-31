from sqlalchemy.orm import Session
from app.models.analysis_view import AnalysisResultView
from typing import List


class AnalysisViewRepository:
    
    @staticmethod
    def get_by_analysis_id(db: Session, analysis_id: int) -> List[AnalysisResultView]:
    
        return db.query(AnalysisResultView)\
            .filter(AnalysisResultView.analysis_id == analysis_id)\
            .all()

