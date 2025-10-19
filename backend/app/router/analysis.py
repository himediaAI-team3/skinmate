from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.services.analysis import AnalysisService
from app.schemas.analysis import AnalysisCreateResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/skin-analysis", tags=["skin-analysis"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_skin_analysis(
    member_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    # Service 호출 (analysis_id만 반환)
    analysis_id = AnalysisService.create_analysis(db, member_id, image)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="이미지 업로드 성공",
        data=AnalysisCreateResponse(analysis_id=analysis_id)
    )



