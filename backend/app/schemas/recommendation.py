from pydantic import BaseModel


class Recommendation(BaseModel):
    """화장품 추천 정보"""
    name: str
    brand: str
    price: float
    file_id: int      # 화장품 이미지 file_id
    buy_url: str      # 구매 링크
    reason: str
    
    class Config:
        from_attributes = True

