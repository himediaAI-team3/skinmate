from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config.database import get_db
from app.services.cosmetic import CosmeticService
from app.schemas.cosmetic import CosmeticSearchResponse, CosmeticDetailResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/cosmetics", tags=["cosmetics"])


@router.get("", response_model=ApiResponse)
def search_cosmetics(
    brand: Optional[str] = Query(None, description="브랜드명 (부분일치)"),
    name: Optional[str] = Query(None, description="제품명 (부분일치)"),
    skin_type: Optional[str] = Query(None, description="피부타입 (부분포함)"),
    category: Optional[str] = Query(None, description="카테고리 (정확일치)"),
    member_id: Optional[int] = Query(None, description="회원 ID (좋아요 여부 확인용)"),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기 (최대 100)"),
    db: Session = Depends(get_db)
):
    """화장품 목록 검색"""
    
    # 서비스 호출
    result = CosmeticService.search_cosmetics(
        db=db,
        brand=brand,
        name=name,
        skin_type=skin_type,
        category=category,
        member_id=member_id,
        page=page,
        size=size
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
