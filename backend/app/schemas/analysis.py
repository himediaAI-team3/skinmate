from pydantic import BaseModel


class AnalysisCreateResponse(BaseModel):
    """피부 분석 생성 응답 (POST용)"""
    analysis_id: int
