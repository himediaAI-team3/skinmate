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


class CosmeticDetailResponse(BaseModel):
    """화장품 상세 정보 응답"""
    cosmetic_id: int
    brand: str
    name: str
    category: Optional[str] = None
    price: Optional[Decimal] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    buy_url: Optional[str] = None
    skin_type: Optional[str] = None
    skin_disease: Optional[str] = None
    main_effect: Optional[str] = None
    care_symptom: Optional[str] = None
    key_ingredient: Optional[str] = None
    ingredients: Optional[str] = None
    file_path: Optional[str] = None
    like_count: int = 0
    is_liked: bool = False

    class Config:
        orm_mode = True