from sqlalchemy.orm import Session
from app.repository.diagnosis import DiagnosisRepository
from app.repository.file import FileRepository
from app.models.diagnosis import Diagnosis
from app.models.entity_type import EntityType


class DiagnosisService:
    
    @staticmethod
    def create_diagnosis(db: Session, analysis_id: int) -> Diagnosis:
        
        # analysis_id로 파일 조회
        file = FileRepository.get_by_entity(db, EntityType.SKIN_ANALYSIS, analysis_id)
        
        # 더미 진단 데이터
        diagnosis_data = {
            "analysis_id": analysis_id,
            "disease_name": "여드름",
            "summary": "염증 후 색소 침착이 관찰됩니다. 피지 분비가 활발하며 모공이 약간 확장되어 있습니다."
        }
        
        return DiagnosisRepository.create(db, diagnosis_data)

