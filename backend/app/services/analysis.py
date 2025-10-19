from sqlalchemy.orm import Session
from fastapi import UploadFile, status
from app.repository.analysis import AnalysisRepository
from app.repository.file import FileRepository
from app.repository.diagnosis import DiagnosisRepository
from app.repository.recommendation import RecommendationRepository
from app.services.file import FileService
from app.services.diagnosis import DiagnosisService
from app.services.recommendation import RecommendationService
from app.models.cosmetic import Cosmetic
from app.schemas.analysis import AnalysisResponse
from app.schemas.recommendation import Recommendation as RecommendationSchema
from app.core.exception import ApiException


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
    
    
    @staticmethod
    def get_analysis_result(db: Session, analysis_id: int) -> AnalysisResponse:
        """
        분석 결과 조회 (GET용)
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            
        Returns:
            AnalysisResponse (전체 결과)
        """
        # 1. 분석 존재 확인
        analysis = AnalysisRepository.get_by_id(db, analysis_id)
        if not analysis:
            raise ApiException(status.HTTP_404_NOT_FOUND, "분석 결과를 찾을 수 없습니다")
        
        # 2. 파일 조회
        file = FileRepository.get_by_analysis_id(db, analysis_id)
        
        # 3. 진단 조회
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
        
        # 4. 추천 목록 조회 (ranking 순)
        recommendations = RecommendationRepository.get_by_analysis_id(db, analysis_id)
        
        # 5. cosmetic JOIN해서 Recommendation 스키마로 변환
        recommendation_list = []
        for rec in recommendations:
            cosmetic = db.query(Cosmetic).filter(Cosmetic.cosmetic_id == rec.cosmetic_id).first()
            if cosmetic:
                recommendation_list.append(RecommendationSchema(
                    name=cosmetic.name,
                    brand=cosmetic.brand,
                    price=float(cosmetic.price),
                    image_url=cosmetic.image_url or "",
                    reason=rec.reason
                ))
        
        # 6. 결과 조합 (products 리스트로 반환)
        return AnalysisResponse(
            analysis_id=analysis_id,
            file_url=file.file_url if file else "",
            disease_name=diagnosis.disease_name if diagnosis else "",
            diagnosis_summary=diagnosis.summary if diagnosis else "",
            products=recommendation_list,
            created_at=analysis.created_at
        )
    
    

