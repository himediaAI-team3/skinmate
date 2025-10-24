from fastapi import APIRouter, Depends, Query, status # Query 추가
from sqlalchemy.orm import Session
from typing import Optional # 새로 추가됨
from app.core.config.database import get_db
from app.services.cosmetic import CosmeticService
from app.schemas.cosmetic import CosmeticSearchResponse, CosmeticDetailResponse, CosmeticSearchParams
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/cosmetics", tags=["cosmetics"])


@router.get("", response_model=ApiResponse)
def search_cosmetics(
    params: CosmeticSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """화장품 목록 검색"""
    
    # 서비스 호출
    result = CosmeticService.search_cosmetics(
        db=db,
        brand=params.brand,
        name=params.name,
        skin_type=params.skin_type,
        category=params.category,
        member_id=params.member_id,
        page=params.page,
        size=params.size
    )
    
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
    member_id: Optional[int] = Query(None, description="회원 ID (좋아요 여부 확인용)"),
    db: Session = Depends(get_db)
):
    """화장품 상세 정보 조회"""
    
    # 서비스 호출
    result = CosmeticService.get_cosmetic_detail(db, cosmetic_id, member_id)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="화장품 상세 조회 성공",
        data=result
    )
