from fastapi import APIRouter, Depends, File, Form, UploadFile, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.core.config.database import get_db
from app.utils.security import get_current_user
from app.services.analysis import AnalysisService
from app.schemas.analysis import AnalysisCreateResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/skin-analysis", tags=["skin-analysis"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_skin_analysis(
    skin_type: Optional[str] = Form(None), # 옵셔널
    min_price: Optional[int] = Form(None), # 옵셔널
    max_price: Optional[int] = Form(None), # 옵셔널

    image: UploadFile = File(...), # 필수값

    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    피부 분석 생성 (이미지 업로드 및 RAG 파이프라인 실행)
    
    **프로세스:**
    1. 이미지 업로드 및 저장
    2. AI 진단 (OpenAI Vision API)
    3. RAG 파이프라인 실행 (Vector 검색 + LLM 추천)
    4. 추천 결과 저장
    
    **Response:**
    - analysis_id: 생성된 분석 ID (결과 조회 시 사용)
    """
    # JWT에서 member_id 추출
    member_id = current_user["member_id"]
    
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
    # 분석 결과 조회
    result = AnalysisService.get_analysis_result(db, analysis_id)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 결과 조회 성공",
        data=result
    )


@router.get("/history", response_model=ApiResponse)
def get_analysis_history(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    disease_name: str = Query(None, description="진단명 필터링 (선택적)"),
    period: str = Query("all", description="기간 필터링 (all/day/week/month)"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    분석 이력 목록 조회
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    - **disease_name**: 진단명 필터링 (선택적)
    - **period**: 기간 필터링 (all/day/week/month, 기본값: all)
    """
    # JWT에서 추출한 사용자 ID 사용
    member_id = current_user["member_id"]
    
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
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    분석 이력 삭제
    
    - **analysis_id**: 분석 ID
    """
    # JWT에서 추출한 사용자 ID 사용
    member_id = current_user["member_id"]
    
    # 이력 삭제 (권한 검증 포함)
    AnalysisService.delete_analysis(db, analysis_id, member_id)
    
    # commit 처리
    db.commit()
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="분석 이력 삭제 성공",
        data=None
    )

