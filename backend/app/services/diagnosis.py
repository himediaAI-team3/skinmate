from sqlalchemy.orm import Session
from app.repository.diagnosis import DiagnosisRepository
from app.models.diagnosis import Diagnosis


class DiagnosisService:
    
    @staticmethod
    def create_diagnosis(db: Session, analysis_id: int) -> Diagnosis:
        """
        피부 진단 생성 (현재: 더미 데이터, 나중: AI 모델)
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            
        Returns:
            Diagnosis 객체
        """
        # 더미 진단 데이터
        diagnosis_data = {
            "analysis_id": analysis_id,
            "disease_name": "여드름",
            "summary": "염증 후 색소 침착이 관찰됩니다. 피지 분비가 활발하며 모공이 약간 확장되어 있습니다."
        }
        
        return DiagnosisRepository.create(db, diagnosis_data)

