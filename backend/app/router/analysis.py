from fastapi import APIRouter, Depends, File, Form, UploadFile, status, Query
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.services.analysis import AnalysisService
from app.schemas.analysis import AnalysisCreateResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/skin-analysis", tags=["skin-analysis"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_skin_analysis(
    member_id: int = Form(...),
    skin_type: str = Form(""),
    min_price: int = Form(0),
    max_price: int = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    # Service 호출 (analysis_id만 반환)
    analysis_id = AnalysisService.create_analysis(
        db=db,
        member_id=member_id,
        image_file=image,
        skin_type=skin_type,
        min_price=min_price,
        max_price=max_price
    )
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_201_CREATED,
        success=True,
        message="이미지 업로드 성공",
        data=AnalysisCreateResponse(analysis_id=analysis_id)
    )


@router.get("/{analysis_id}", response_model=ApiResponse)
def get_skin_analysis_result(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    피부 분석 결과 조회
    
    - **analysis_id**: 분석 ID
    """
    # 전체 결과 조회
    result = AnalysisService.get_analysis_result(db, analysis_id)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 결과 조회 성공",
        data=result
    )


@router.get("/history/{member_id}", response_model=ApiResponse)
def get_analysis_history(
    member_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    disease_name: str = Query(None, description="진단명 필터링 (선택적)"),
    period: str = Query("all", description="기간 필터링 (all/day/week/month)"),
    db: Session = Depends(get_db)
):
    """
    분석 이력 목록 조회
    
    - **member_id**: 회원 ID
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    - **disease_name**: 진단명 필터링 (선택적)
    - **period**: 기간 필터링 (all/day/week/month, 기본값: all)
    """
    # 이력 목록 조회
    result = AnalysisService.get_analysis_history(db, member_id, page, size, disease_name, period)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 이력 조회 성공",
        data=result
    )


@router.delete("/{analysis_id}", response_model=ApiResponse)
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    분석 이력 삭제
    
    - **analysis_id**: 분석 ID
    """
    # 이력 삭제
    AnalysisService.delete_analysis(db, analysis_id)
    
    # commit 처리
    db.commit()
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 이력 삭제 성공",
        data=None
    )

    # 분석 이력 조회 및 삭제 엔드포인트

