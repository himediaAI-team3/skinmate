from sqlalchemy.orm import Session
from fastapi import UploadFile, status
from app.repository.analysis import AnalysisRepository
from app.repository.analysis_view import AnalysisViewRepository
from app.services.file import FileService
from app.services.diagnosis import DiagnosisService
from app.services.recommendation import RecommendationService
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
        
        # 1. DB View에서 데이터 조회 (ranking 순 정렬됨)
        view_results = AnalysisViewRepository.get_by_analysis_id(db, analysis_id)
        
        if not view_results:
            raise ApiException(status.HTTP_404_NOT_FOUND, "분석 결과를 찾을 수 없습니다")
        
        # 2. 첫 번째 row에서 기본 정보 추출
        first_row = view_results[0]
        
        # 3. 추천 제품 리스트 구성 (cosmetic_id가 있는 row만)
        recommendation_list = []
        for row in view_results:
            if row.cosmetic_id:  # cosmetic이 존재하는 경우만
                recommendation_list.append(RecommendationSchema(
                    name=row.cosmetic_name or "",
                    brand=row.brand or "",
                    price=float(row.price) if row.price else 0,
                    file_id=row.cosmetic_file_id or 0,
                    buy_url=row.buy_url or "",
                    reason=row.reason or ""
                ))
        
        # 4. 응답 반환
        return AnalysisResponse(
            analysis_id=first_row.analysis_id,
            file_id=first_row.skin_file_id or 0, # 유저가 업로드한 피부 이미지파일 ID
            disease_name=first_row.disease_name or "",
            diagnosis_summary=first_row.diagnosis_summary or "",
            products=recommendation_list,
            created_at=first_row.analysis_created_at
        )
    
    

