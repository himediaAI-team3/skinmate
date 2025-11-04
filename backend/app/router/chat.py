"""
Chat API Router
- AI Agent와 대화 기능 제공
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.config.database import get_db
from app.services.agent_service import AgentService
from app.schemas.response import ApiResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """채팅 요청"""
    member_id: int = Field(..., description="회원 ID")
    message: str = Field(..., description="사용자 메시지")
    thread_id: Optional[str] = Field(None, description="대화 thread ID (선택)")


class ChatResponse(BaseModel):
    """채팅 응답"""
    response: str = Field(..., description="AI 응답")
    thread_id: str = Field(..., description="대화 thread ID")


@router.post("", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    AI Agent와 대화
    
    - **member_id**: 회원 ID (필수)
    - **message**: 사용자 메시지 (필수)
    - **thread_id**: 대화 thread ID (선택, 이전 대화 이어가기)
    
    ## 사용 예시
    
    ### 1. 새로운 대화 시작
    ```json
    {
        "member_id": 1,
        "message": "안녕하세요!"
    }
    ```
    
    ### 2. 진단 이력 조회
    ```json
    {
        "member_id": 1,
        "message": "내 최근 진단 결과 뭐였지?",
        "thread_id": "thread_1_abc123"
    }
    ```
    
    ### 3. 추천 제품 조회
    ```json
    {
        "member_id": 1,
        "message": "추천받은 화장품 보여줘"
    }
    ```
    """
    try:
        logger.info(f"Chat 요청: member_id={request.member_id}, message={request.message[:50]}...")
        
        # Agent Service 호출
        result = AgentService.chat(
            db=db,
            member_id=request.member_id,
            message=request.message,
            thread_id=request.thread_id
        )
        
        # ApiResponse로 감싸서 반환
        return ApiResponse(
            code=status.HTTP_200_OK,
            success=True,
            message="채팅 성공",
            data=ChatResponse(
                response=result["response"],
                thread_id=result["thread_id"]
            )
        )
        
    except Exception as e:
        logger.error(f"Chat 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return ApiResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            message=f"채팅 처리 중 오류가 발생했습니다: {str(e)}",
            data=None
        )

