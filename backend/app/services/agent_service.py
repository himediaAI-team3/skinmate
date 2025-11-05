"""
LangGraph 기반 AI Agent 서비스
"""
import secrets
from typing import Tuple
from sqlalchemy.orm import Session
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.services.chat_tools import TOOLS, set_tool_context
from app.utils.prompt import load_prompt
from app.core.config.llm import get_llm, TEMPERATURE_CHAT


class AgentService:
    """LangGraph 기반 Agent 서비스"""
    
    # 메모리 저장소 (서버 재시작 시 초기화)
    _memory = MemorySaver()
    
    @staticmethod
    def _create_agent():
        """Agent 생성 (LLM + Tools + Checkpointer)"""
        llm = get_llm(TEMPERATURE_CHAT)
        
        # 프롬프트 로드
        system_prompt = load_prompt("chat.yaml")
        
        agent = create_react_agent(
            llm,
            TOOLS,
            checkpointer=AgentService._memory,
            state_modifier=system_prompt
        )
        
        return agent
    
    @staticmethod
    def _validate_thread_id(member_id: int, thread_id: str) -> None:
        """
        thread_id 권한 검증
        
        Args:
            member_id: JWT에서 추출한 사용자 ID
            thread_id: 요청한 thread_id (형식: thread_{member_id}_{random})
        
        Raises:
            ValueError: thread_id가 유효하지 않은 경우
        """
        if not thread_id.startswith(f"thread_{member_id}_"):
            raise ValueError(
                "유효하지 않은 thread_id입니다. 다른 사용자의 대화에 접근할 수 없습니다."
            )
    
    @staticmethod
    def _generate_thread_id(member_id: int) -> str:
        """
        새로운 thread_id 생성
        
        Args:
            member_id: 사용자 ID
        
        Returns:
            str: 생성된 thread_id (형식: thread_{member_id}_{random_hex})
        """
        random_hex = secrets.token_hex(4)
        return f"thread_{member_id}_{random_hex}"
    
    @staticmethod
    def chat(db: Session, member_id: int, message: str, thread_id: str = None) -> Tuple[str, str]:
        """
        사용자와 대화 (Tool 호출 포함)
        
        Args:
            db: DB 세션
            member_id: JWT에서 추출한 사용자 ID
            message: 사용자 메시지
            thread_id: 대화 스레드 ID (선택사항)
        
        Returns:
            (response, thread_id): AI 응답과 thread_id
        
        Raises:
            ValueError: thread_id 권한 검증 실패 시
        """
        # 1. thread_id 처리
        if thread_id:
            # 기존 thread_id 검증
            AgentService._validate_thread_id(member_id, thread_id)
        else:
            # 새로운 thread_id 생성
            thread_id = AgentService._generate_thread_id(member_id)
        
        # 2. Tool 컨텍스트 설정 (DB 세션, member_id)
        set_tool_context(db, member_id)
        
        # 3. Agent 생성 및 실행
        agent = AgentService._create_agent()
        
        # 4. 대화 실행 (thread_id로 이전 대화 이력 유지)
        config = {"configurable": {"thread_id": thread_id}}
        result = agent.invoke({"messages": [("user", message)]}, config)
        
        # 5. 응답 추출
        ai_response = result["messages"][-1].content
        
        return ai_response, thread_id