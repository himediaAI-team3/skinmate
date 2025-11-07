from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.services.cosmetic import CosmeticService
from app.schemas.cosmetic import CosmeticSearchParams
from app.schemas.response import ApiResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/cosmetics", tags=["cosmetics"])


@router.get("", response_model=ApiResponse)
def search_cosmetics(
    params: CosmeticSearchParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """화장품 목록 검색"""
    
    # JWT 토큰에서 추출한 member_id 사용
    member_id = current_user["member_id"]
    params.member_id = member_id
    
    # 서비스 호출
    result = CosmeticService.search_cosmetics(db=db, params=params)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="화장품 목록 조회 성공",
        data=result
    )


@router.get("/{cosmetic_id}", response_model=ApiResponse)
def get_cosmetic_detail(
    cosmetic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """화장품 상세 정보 조회"""
    
    # JWT 토큰에서 추출한 member_id 사용
    member_id = current_user["member_id"]
    
    # 서비스 호출
    result = CosmeticService.get_cosmetic_detail(db, cosmetic_id, member_id)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="화장품 상세 조회 성공",
        data=result
    )
