from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .recommendation import Recommendation


class AnalysisCreateResponse(BaseModel):
    """피부 분석 생성 응답 (POST용)"""
    analysis_id: int


class AnalysisResponse(BaseModel):
    """피부 분석 결과 응답 (GET용)"""
    analysis_id: int
    file_url: str  # 피부 이미지 URL
    disease_name: str
    diagnosis_summary: str
    products: List[Recommendation]  # TOP 3 화장품 리스트
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
