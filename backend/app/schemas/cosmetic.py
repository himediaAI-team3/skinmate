from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class CosmeticSearchItem(BaseModel):
    """화장품 목록 검색 결과 아이템"""
    cosmetic_id: int
    name: str
    brand: str
    category: Optional[str] = None
    price: Optional[Decimal] = None
    file_path: Optional[str] = None
    like_count: int
    is_liked: bool

    class Config:
        orm_mode = True


class CosmeticSearchResponse(BaseModel):
    """화장품 목록 검색 응답"""
    page: int
    size: int
    total: int
    items: List[CosmeticSearchItem]

    class Config:
        orm_mode = True
