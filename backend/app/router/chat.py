"""
채팅 API 라우터
"""
from fastapi import APIRouter, Depends, status as http_status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.utils.security import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.response import ApiResponse
from app.services.agent_service import AgentService
from app.core.exception.exceptions import ApiException


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ApiResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI Agent와 대화하기
    
    - **message**: 사용자 메시지 (필수)
    - **thread_id**: 대화 스레드 ID (선택사항, 이전 대화 이어가기)
    
    **사용 예시:**
    1. 새로운 대화 시작: thread_id 없이 요청
    2. 이전 대화 이어가기: 이전 응답의 thread_id를 포함하여 요청
    
    **보안:**
    - JWT 토큰 필수 (Authorization: Bearer <token>)
    - thread_id는 사용자별로 격리 (다른 사용자의 대화 접근 불가)
    """
    member_id = current_user["member_id"]
    
    try:
        # Agent 서비스 호출
        ai_response, thread_id = AgentService.chat(
            db=db,
            member_id=member_id,
            message=request.message,
            thread_id=request.thread_id
        )
        
        return ApiResponse(
            code=200,
            success=True,
            message="채팅 성공",
            data=ChatResponse(
                response=ai_response,
                thread_id=thread_id
            )
        )
    
    except ValueError as e:
        # thread_id 권한 검증 실패
        raise ApiException(
            http_status.HTTP_403_FORBIDDEN,
            str(e)
        )
    
    except Exception as e:
        # 기타 오류
        raise ApiException(
            http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"채팅 중 오류가 발생했습니다: {str(e)}"
        )