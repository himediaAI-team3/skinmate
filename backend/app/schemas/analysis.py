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
    file_id: int  # 피부 이미지 파일 ID (GET /api/files/{file_id}로 조회)
    disease_name: str
    diagnosis_summary: str
    products: List[Recommendation]  # TOP 3 화장품 리스트
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnalysisHistoryItem(BaseModel):
    """분석 이력 목록의 개별 항목"""
    analysis_id: int
    disease_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisHistoryResponse(BaseModel):
    """페이징된 분석 이력 목록 응답"""
    items: List[AnalysisHistoryItem]
    total: int
    page: int
    size: int

# 분석 이력 관련 스키마
