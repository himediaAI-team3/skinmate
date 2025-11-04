from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Dict
from app.core.config.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.like import LikeToggleResponse
from app.services.like import LikeService
from app.utils.security import get_current_user


router = APIRouter(prefix="/api/cosmetics", tags=["likes"])


@router.get("/likes", response_model=ApiResponse)
def get_liked_cosmetics(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(5, ge=1, le=100, description="페이지 크기"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    좋아요한 화장품 목록 조회
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 5, 최대: 100)
    """
    # JWT에서 추출한 사용자 ID 사용
    member_id = current_user["member_id"]
    
    # 좋아요 목록 조회
    result = LikeService.get_liked_cosmetics(db, member_id, page, size)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="좋아요 목록 조회 성공",
        data=result
    )


@router.post("/{cosmetic_id}/likes", response_model=ApiResponse)
def toggle_like(
    cosmetic_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """좋아요 토글 (INSERT 시도 → 실패 시 DELETE)"""
    # JWT에서 추출한 사용자 ID 사용
    member_id = current_user["member_id"]
    
    result = LikeService.toggle_like(db, member_id, cosmetic_id)
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="좋아요 토글 완료",
        data=LikeToggleResponse(**result)
    )