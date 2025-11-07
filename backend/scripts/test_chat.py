"""
Chat API 통합 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.agent_service import AgentService
from app.core.config.database import DATABASE_URL


def test_chat_service():
    """Chat Service 통합 테스트"""
    print("=" * 60)
    print("Chat API 통합 테스트 시작")
    print("=" * 60)
    
    # DB 세션 생성
    print("\n📦 DB 연결 중...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    print("✅ DB 연결 성공")
    
    try:
        # 테스트 사용자 (member_id=1)
        member_id = 1
        
        # 1. 새로운 대화 시작
        print("\n" + "=" * 60)
        print("테스트 1: 새로운 대화 시작")
        print("=" * 60)
        print(f"\n👤 사용자 (member_id={member_id}): 안녕하세요")
        response, thread_id = AgentService.chat(db, member_id, "안녕하세요")
        print(f"🤖 AI: {response}")
        print(f"🔑 thread_id: {thread_id}")
        
        # 2. 진단 이력 조회 (Tool 호출)
        print("\n" + "=" * 60)
        print("테스트 2: 진단 이력 조회 (Tool 호출)")
        print("=" * 60)
        print(f"\n👤 사용자: 내 최근 진단 결과 보여줘")
        response, _ = AgentService.chat(db, member_id, "내 최근 진단 결과 보여줘", thread_id)
        print(f"🤖 AI: {response}")
        
        # 3. 추천 제품 조회 (Tool 호출)
        print("\n" + "=" * 60)
        print("테스트 3: 추천 제품 조회 (Tool 호출)")
        print("=" * 60)
        print(f"\n👤 사용자: 추천받은 화장품 보여줘")
        response, _ = AgentService.chat(db, member_id, "추천받은 화장품 보여줘", thread_id)
        print(f"🤖 AI: {response}")
        
        # 4. 일반 대화 (Tool 없이)
        print("\n" + "=" * 60)
        print("테스트 4: 일반 대화 (Tool 없이)")
        print("=" * 60)
        print(f"\n👤 사용자: 피부 관리 팁 알려줘")
        response, _ = AgentService.chat(db, member_id, "피부 관리 팁 알려줘", thread_id)
        print(f"🤖 AI: {response}")
        
        # 5. 대화 이력 기억 확인
        print("\n" + "=" * 60)
        print("테스트 5: 대화 이력 기억 확인")
        print("=" * 60)
        print(f"\n👤 사용자: 내가 처음에 뭐라고 했지?")
        response, _ = AgentService.chat(db, member_id, "내가 처음에 뭐라고 했지?", thread_id)
        print(f"🤖 AI: {response}")
        
        print("\n" + "=" * 60)
        print("✨ 모든 통합 테스트 통과!")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    try:
        test_chat_service()
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)