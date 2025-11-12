from fastapi import APIRouter, Depends, File, Form, UploadFile, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Optional, Literal
from app.core.config.database import get_db
from app.utils.security import get_current_user
from app.services.analysis import AnalysisService
from app.schemas.analysis import AnalysisCreateResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/skin-analysis", tags=["skin-analysis"])

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_skin_analysis(
    skin_type: Optional[str] = Form(None),
    min_price: Optional[int] = Form(None),
    max_price: Optional[int] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    member_id = current_user["member_id"]
    analysis_id = AnalysisService.create_analysis(
        db=db,
        member_id=member_id,
        image_file=image,
        skin_type=skin_type,
        min_price=min_price,
        max_price=max_price,
    )
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="이미지 업로드 성공",
        data=AnalysisCreateResponse(analysis_id=analysis_id),
    )

# ✅ 정적 라우트(히스토리)를 동적 라우트보다 먼저 등록
@router.get("/history", response_model=ApiResponse)
def get_analysis_history(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    disease_name: Optional[str] = Query(None, description="진단명 필터링 (선택적)"),
    period: Literal["all", "day", "week", "month"] = Query("all", description="기간 필터링"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    분석 이력 목록 조회
    - page: 기본 1
    - size: 기본 10 (최대 100)
    - disease_name: 선택
    - period: all/day/week/month (기본 all)
    """
    member_id = current_user["member_id"]
    result = AnalysisService.get_analysis_history(db, member_id, page, size, disease_name, period)
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 이력 조회 성공",
        data=result,
    )

# ✅ 동적 라우트는 뒤로
@router.get("/{analysis_id}", response_model=ApiResponse)
def get_skin_analysis_result(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    result = AnalysisService.get_analysis_result(db, analysis_id)
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 결과 조회 성공",
        data=result,
    )

@router.delete("/{analysis_id}", response_model=ApiResponse)
def delete_analysis(
    analysis_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    분석 이력 삭제
    """
    member_id = current_user["member_id"]
    AnalysisService.delete_analysis(db, analysis_id, member_id)
    db.commit()
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 이력 삭제 성공",
        data=None,
    )
