from sqlalchemy.orm import Session
from app.models.diagnosis import Diagnosis


class DiagnosisRepository:
    
    @staticmethod
    def create(db: Session, diagnosis_data: dict) -> Diagnosis:
        """진단 정보 저장"""
        diagnosis = Diagnosis(**diagnosis_data)
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis
    
    @staticmethod
    def get_by_analysis_id(db: Session, analysis_id: int) -> Diagnosis:
        return db.query(Diagnosis).filter(Diagnosis.analysis_id == analysis_id).first()
    
    @staticmethod
    def delete_by_analysis_id(db: Session, analysis_id: int) -> int:
        """분석 ID로 진단 정보 삭제"""
        deleted = db.query(Diagnosis).filter(Diagnosis.analysis_id == analysis_id).delete()
        return deleted

