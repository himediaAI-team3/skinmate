"""
LangGraph AI Agent Service
- Agent 초기화 및 대화 처리
- InMemorySaver로 대화 이력 관리
"""
import os
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.services.chat_tools import get_chat_tools
import logging

logger = logging.getLogger(__name__)


class AgentService:
    """AI Agent 관리 서비스"""
    
    # 전역 메모리 (서버 재시작 시 초기화됨)
    _memory = MemorySaver()
    
    @staticmethod
    def create_agent(db: Session, member_id: int):
        """
        Agent 생성
        
        Args:
            db: 데이터베이스 세션
            member_id: 회원 ID
            
        Returns:
            agent: 실행 가능한 Agent
        """
        # LLM 초기화
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,  # 대화형이므로 약간 높게
        )
        
        # Tools 준비 (member_id closure 포함)
        tools = get_chat_tools(db, member_id)
        
        # Agent 생성 (React Agent)
        agent = create_react_agent(
            llm,
            tools=tools,
            checkpointer=AgentService._memory
        )
        
        logger.info(f"Agent 생성 완료 (member_id: {member_id})")
        
        return agent
    
    @staticmethod
    def chat(db: Session, member_id: int, message: str, thread_id: str = None) -> dict:
        """
        사용자와 대화
        
        Args:
            db: 데이터베이스 세션
            member_id: 회원 ID
            message: 사용자 메시지
            thread_id: 대화 thread ID (없으면 자동 생성)
            
        Returns:
            dict: {response: str, thread_id: str}
        """
        try:
            # thread_id 생성 또는 검증
            if not thread_id:
                # 새로운 thread 생성 (member_id 포함하여 고유성 보장)
                thread_id = f"thread_{member_id}_{int(os.urandom(4).hex(), 16)}"
            else:
                # 기존 thread_id 보안 검증: member_id가 일치하는지 확인
                if not thread_id.startswith(f"thread_{member_id}_"):
                    raise ValueError(
                        f"유효하지 않은 thread_id입니다. "
                        f"다른 사용자의 대화에 접근할 수 없습니다."
                    )
            
            # Agent 생성
            agent = AgentService.create_agent(db, member_id)
            
            # System Prompt 추가
            system_prompt = """당신은 피부 관리 전문가 AI 어시스턴트입니다.
사용자의 피부 진단 결과와 추천 화장품에 대해 친절하게 안내합니다.

다음 Tool을 활용할 수 있습니다:
- get_my_diagnosis_history_impl: 최근 진단 이력 조회
- get_recommended_products_impl: 추천 제품 조회
- recommend_by_symptom_impl: 증상별 화장품 추천
- request_rediagnosis_impl: 재진단 요청 안내
- get_product_detail_impl: 제품 상세 정보 조회

사용자가 진단 결과나 추천 제품을 물어보면 적절한 Tool을 사용하세요.
사용자가 "아까 뭐라고 했지?" 같은 과거 대화를 물어볼 때는 대화 이력이 없으므로 친절하게 첫 대화임을 안내하세요.
답변은 친절하고 명확하게 작성하며, 한국어로 응답합니다."""
            
            # 메시지 구성: 새 스레드면 system+user, 기존 스레드면 user만 전달하여 메모리 이력 사용
            is_new_thread = not (thread_id and thread_id.startswith(f"thread_{member_id}_"))
            if is_new_thread:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            else:
                messages = [
                    {"role": "user", "content": message}
                ]
            
            # Agent 실행
            config = {"configurable": {"thread_id": thread_id}}
            logger.info(f"Agent 실행 시작 (thread_id: {thread_id}, message: {message[:50]}...)")
            
            result = agent.invoke(
                {"messages": messages},
                config=config
            )
            
            logger.info(f"Agent 실행 완료, 응답 추출 중... (thread_id: {thread_id})")
            
            # 응답 추출
            response_content = result['messages'][-1].content
            
            logger.info(f"Agent 응답 완료 (thread_id: {thread_id}, response_length: {len(response_content)})")
            
            return {
                "response": response_content,
                "thread_id": thread_id
            }
            
        except Exception as e:
            logger.error(f"Agent 실행 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise e

