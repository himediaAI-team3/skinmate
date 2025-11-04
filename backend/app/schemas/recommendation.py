from pydantic import BaseModel
from typing import Optional


class Recommendation(BaseModel):
    """화장품 추천 정보"""
    name: str
    brand: str
    price: float
    file_path: Optional[str] = None  # 화장품 이미지 경로
    buy_url: str      # 구매 링크
    reason: str
    
    class Config:
        from_attributes = True

