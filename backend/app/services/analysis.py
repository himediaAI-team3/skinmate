from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.repository.analysis import AnalysisRepository
from app.services.file import FileService
from app.services.diagnosis import DiagnosisService
from app.services.recommendation import RecommendationService


class AnalysisService:
    
    @staticmethod
    def create_analysis(db: Session, member_id: int, image_file: UploadFile) -> int:
        """
        피부 분석 생성 (POST용)
        
        Args:
            db: 데이터베이스 세션
            member_id: 회원 ID
            image_file: 업로드 이미지
            
        Returns:
            analysis_id (생성된 분석 ID)
        """
        # 1. skin_analysis 생성
        analysis = AnalysisRepository.create(db, {"member_id": member_id})
        analysis_id = analysis.analysis_id
        
        # 2. 파일 업로드 (FileService 호출)
        FileService.upload_and_save(db, analysis_id, image_file)
        
        # 3. 진단 생성 (더미 데이터 -> 추후 파인튜닝 모델 적용)
        DiagnosisService.create_diagnosis(db, analysis_id)
        
        # 4. 추천 생성 (더미 데이터 -> 추후 RAG 파이프라인 구축)
        RecommendationService.create_recommendations(db, analysis_id, member_id)
        
        # 5. analysis_id만 반환
        return analysis_id
    
    

