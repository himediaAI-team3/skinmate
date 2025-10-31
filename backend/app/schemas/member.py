from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MemberCreate(BaseModel):
    """개인정보 입력 요청 스키마"""
    skin_type: Optional[str] = Field(None, description="피부 타입 (지성, 건성, 복합성, 민감성 등)")
    min_price: Optional[int] = Field(None, ge=0, description="최소 선호 가격대")
    max_price: Optional[int] = Field(None, ge=0, description="최대 선호 가격대")
    gender: Optional[str] = Field(None, description="성별 (남성, 여성)")
    age_group: Optional[int] = Field(None, description="나이대 (10, 20, 30, 40, 50)")

    class Config:
        json_schema_extra = {
            "example": {
                "skin_type": "지성",
                "min_price": 10000,
                "max_price": 50000,
                "gender": "여성",
                "age_group": 20
            }
        }


class MemberResponse(BaseModel):
    """회원 정보 응답 스키마"""
    member_id: int
    skin_type: str
    min_price: int
    max_price: int
    gender: str
    age_group: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델 → Pydantic 자동 변환

