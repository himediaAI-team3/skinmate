"""
LangGraph Agent 기본 호환성 테스트
- 멘토님 예시 코드 기반
- langgraph + langchain 동작 확인
- OpenAI API 연동 확인
"""
import os
import sys

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

try:
    from langchain.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import MemorySaver
    print("[OK] 모든 패키지 import 성공")
except ImportError as e:
    print(f"[ERROR] Import 실패: {e}")
    print("\n다음 명령어로 패키지를 설치하세요:")
    print("pip install langgraph")
    sys.exit(1)


# 간단한 테스트 Tool 정의
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.
    
    Args:
        a: First int
        b: Second int
    """
    print(f"[LOG] multiply {a}, {b}")
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds a and b.
    
    Args:
        a: First int
        b: Second int
    """
    print(f"[LOG] add {a}, {b}")
    return a + b


def test_basic_agent():
    """기본 Agent 테스트"""
    print("\n" + "="*80)
    print("LangGraph Agent 기본 테스트")
    print("="*80)
    
    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 추가하세요.")
        return False
    
    print(f"[OK] OPENAI_API_KEY 확인 완료 (길이: {len(api_key)})")
    
    # LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key
    )
    print("[OK] ChatOpenAI 초기화 완료")
    
    # Tools 준비
    tools = [add, multiply]
    
    # Agent 생성
    memory = MemorySaver()
    agent = create_react_agent(llm, tools, checkpointer=memory)
    print("[OK] Agent 생성 완료")
    
    # 테스트 1: 간단한 대화
    print("\n[테스트 1] 간단한 인사")
    config = {"configurable": {"thread_id": "test_thread_1"}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Hello! Nice to meet you."}]},
        config=config
    )
    response = result['messages'][-1].content
    print(f"응답: {response[:100]}...")
    
    # 테스트 2: Tool 사용
    print("\n[테스트 2] Tool 호출 (계산)")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is 15 multiplied by 7?"}]},
        config=config
    )
    response = result['messages'][-1].content
    print(f"응답: {response}")
    
    # 테스트 3: 대화 이력 유지 확인
    print("\n[테스트 3] 대화 이력 유지 (같은 thread_id)")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What did you just calculate?"}]},
        config=config
    )
    response = result['messages'][-1].content
    print(f"응답: {response}")
    
    # 테스트 4: 새로운 thread (대화 이력 없음)
    print("\n[테스트 4] 새로운 thread_id (대화 이력 없음)")
    config_new = {"configurable": {"thread_id": "test_thread_2"}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What did you just calculate?"}]},
        config=config_new
    )
    response = result['messages'][-1].content
    print(f"응답: {response}")
    
    print("\n" + "="*80)
    print("[OK] 모든 테스트 통과!")
    print("="*80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_basic_agent()
        if success:
            print("\n[OK] langgraph 호환성 검증 완료")
            print("   -> requirements.txt에 langgraph를 추가할 수 있습니다.")
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

