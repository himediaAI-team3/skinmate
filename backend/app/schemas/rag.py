from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DiagnosisInfo(BaseModel):
    disease_name: str = Field(default="", min_length=0)
    summary: str = Field(default="", min_length=0)
    skin_type: Optional[str] = Field(default=None, min_length=0)
    min_price: Optional[int] = None
    max_price: Optional[int] = None


class PriceFilter(BaseModel):
    gte: int
    lte: int


class QuerySpec(BaseModel):
    text_query: str = Field(min_length=1)
    keywords: list[str] = Field(min_length=1, max_length=10)
    price_filter: Optional[PriceFilter] = None


class RecommendationItem(BaseModel):
    cosmetic_id: int
    ranking: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=170)


__all__ = [
    "DiagnosisInfo",
    "PriceFilter",
    "QuerySpec",
    "RecommendationItem",
]


