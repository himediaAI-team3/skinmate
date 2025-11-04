from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class CosmeticSearchParams(BaseModel):
    """화장품 목록 검색 파라미터"""
    brand: Optional[str] = Field(None, description="브랜드명 (부분일치)")
    name: Optional[str] = Field(None, description="제품명 (부분일치)")
    skin_type: Optional[str] = Field(None, description="피부타입 (부분포함)")
    category: Optional[str] = Field(None, description="카테고리 (정확일치)")
    member_id: Optional[int] = Field(None, description="회원 ID (좋아요 여부용)")
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")

    class Config:
        json_schema_extra = {
            "example": {
                "brand": "제로이드",
                "name": "크림",
                "skin_type": "건성",
                "category": "로션/크림/올인원",
                "member_id": 1,
                "page": 1,
                "size": 10
            }
        }


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