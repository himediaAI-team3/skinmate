from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.like import LikeToggleResponse, LikeCountResponse, LikeStatusResponse
from app.services.like import LikeService


router = APIRouter(prefix="/api/likes", tags=["likes"])


@router.post("/{cosmetic_id}/toggle", response_model=ApiResponse)
def toggle_like(cosmetic_id: int, member_id: int, db: Session = Depends(get_db)):
    """좋아요 토글 (INSERT 시도 → 실패 시 DELETE)"""
    result = LikeService.toggle_like(db, member_id, cosmetic_id)
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="좋아요 토글 완료",
        data=LikeToggleResponse(**result)
    )


# @router.get("/{cosmetic_id}/count", response_model=ApiResponse)
# def get_like_count(cosmetic_id: int, db: Session = Depends(get_db)):
#     """화장품별 좋아요 개수 조회"""
#     result = LikeService.get_like_count(db, cosmetic_id)
#     return ApiResponse(
#         code=status.HTTP_200_OK,
#         success=True,
#         message="좋아요 개수 조회 완료",
#         data=LikeCountResponse(**result)
#     )


# @router.get("/{cosmetic_id}", response_model=ApiResponse)
# def get_like_info(cosmetic_id: int, member_id: int, db: Session = Depends(get_db)):
#     """좋아요 여부와 개수 조회"""
#     result = LikeService.get_like_info(db, member_id, cosmetic_id)
#     return ApiResponse(
#         code=status.HTTP_200_OK,
#         success=True,
#         message="좋아요 정보 조회 완료",
#         data=LikeStatusResponse(**result)
#     )
