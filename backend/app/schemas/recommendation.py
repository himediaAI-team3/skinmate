from pydantic import BaseModel


class Recommendation(BaseModel):
    """화장품 추천 정보"""
    name: str
    brand: str
    price: float
    image_url: str
    reason: str
    
    class Config:
        from_attributes = True

