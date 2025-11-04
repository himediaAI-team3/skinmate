from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class LikeToggleResponse(BaseModel):
    """좋아요 토글 응답"""
    is_liked: bool
    like_count: int


class LikeCountResponse(BaseModel):
    """좋아요 개수 응답"""
    like_count: int


class LikeStatusResponse(BaseModel):
    """좋아요 상태 응답 (여부 + 개수)"""
    is_liked: bool
    like_count: int


class LikedCosmeticItem(BaseModel):
    """좋아요한 화장품 개별 항목"""
    cosmetic_id: int
    name: str
    brand: str
    price: Optional[Decimal] = None
    file_path: Optional[str] = None
    is_liked: bool = True

    class Config:
        from_attributes = True


class LikedCosmeticsResponse(BaseModel):
    """좋아요한 화장품 목록 응답 (페이징)"""
    items: List[LikedCosmeticItem]
    total: int
    page: int
    size: int
