"""
채팅 API 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """채팅 요청"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    thread_id: Optional[str] = Field(None, description="대화 스레드 ID (이전 대화 이어가기)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "내 최근 진단 결과 뭐였지?",
                "thread_id": "thread_1_abc123"
            }
        }


class ChatResponse(BaseModel):
    """채팅 응답"""
    response: str = Field(..., description="AI 응답 메시지")
    thread_id: str = Field(..., description="대화 스레드 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "최근 진단 결과는 다음과 같습니다:\n- 진단일: 2025년 11월 03일\n- 진단명: 주사\n...",
                "thread_id": "thread_1_abc123"
            }
        }

