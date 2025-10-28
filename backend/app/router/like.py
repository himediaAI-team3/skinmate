from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.like import LikeToggleRequest, LikeToggleResponse, LikeCountResponse, LikeStatusResponse, LikedCosmeticsResponse
from app.services.like import LikeService


router = APIRouter(prefix="/api/cosmetics", tags=["likes"])


@router.get("/likes/{member_id}", response_model=ApiResponse)
def get_liked_cosmetics(
    member_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(5, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db)
):
    """
    좋아요한 화장품 목록 조회
    
    - **member_id**: 회원 ID (Path Parameter)
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 5, 최대: 100)
    """
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
def toggle_like(cosmetic_id: int, request: LikeToggleRequest, db: Session = Depends(get_db)):
    """좋아요 토글 (INSERT 시도 → 실패 시 DELETE)"""
    result = LikeService.toggle_like(db, request.member_id, cosmetic_id)
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
