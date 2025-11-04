"""
AI Agent 보안 테스트
- thread_id 권한 검증
- 다른 사용자의 대화 접근 차단 확인
"""
import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.database import SessionLocal
from app.services.agent_service import AgentService
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# httpx HTTP 요청 로그 숨기기
logging.getLogger("httpx").setLevel(logging.WARNING)


def test_thread_security():
    """thread_id 보안 테스트"""
    print("\n" + "="*80)
    print("AI Agent thread_id 보안 테스트")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # 테스트 1: 사용자 1이 새로운 대화 시작
        print("\n[테스트 1] 사용자 1이 새로운 대화 시작")
        print("-" * 80)
        
        result1 = AgentService.chat(
            db=db,
            member_id=1,
            message="안녕하세요"
        )
        
        thread_id_user1 = result1['thread_id']
        print(f"사용자 1의 thread_id: {thread_id_user1}")
        print(f"응답: {result1['response'][:50]}...")
        
        # 검증: thread_id가 member_id를 포함하는지 확인
        assert thread_id_user1.startswith("thread_1_"), "thread_id는 member_id를 포함해야 합니다"
        print("[OK] thread_id가 member_id를 포함합니다")
        
        # 테스트 2: 사용자 1이 같은 thread로 계속 대화
        print("\n[테스트 2] 사용자 1이 같은 thread로 계속 대화")
        print("-" * 80)
        
        result2 = AgentService.chat(
            db=db,
            member_id=1,
            message="내 진단 이력 보여줘",
            thread_id=thread_id_user1  # 같은 thread 사용
        )
        
        print(f"응답: {result2['response'][:50]}...")
        print("[OK] 같은 사용자의 thread_id 재사용 성공")
        
        # 테스트 3: 사용자 2가 사용자 1의 thread_id로 접근 시도 (차단되어야 함)
        print("\n[테스트 3] 사용자 2가 사용자 1의 thread_id로 접근 시도")
        print("-" * 80)
        print(f"사용자 2가 사용자 1의 thread_id({thread_id_user1})로 접근 시도...")
        
        try:
            result3 = AgentService.chat(
                db=db,
                member_id=2,  # 다른 사용자
                message="내 진단 이력 보여줘",
                thread_id=thread_id_user1  # 사용자 1의 thread_id
            )
            
            # 여기까지 오면 안됨
            print("[ERROR] 다른 사용자의 thread_id 접근이 차단되지 않았습니다!")
            return False
            
        except ValueError as e:
            print(f"[OK] 접근 차단됨: {e}")
        
        # 테스트 4: 사용자 2의 독립적인 대화
        print("\n[테스트 4] 사용자 2의 독립적인 대화")
        print("-" * 80)
        
        result4 = AgentService.chat(
            db=db,
            member_id=2,
            message="안녕하세요"
        )
        
        thread_id_user2 = result4['thread_id']
        print(f"사용자 2의 thread_id: {thread_id_user2}")
        print(f"응답: {result4['response'][:50]}...")
        
        # 검증: thread_id가 member_id를 포함하는지 확인
        assert thread_id_user2.startswith("thread_2_"), "thread_id는 member_id를 포함해야 합니다"
        print("[OK] 사용자 2의 thread_id가 독립적으로 생성되었습니다")
        
        # 검증: 두 사용자의 thread_id가 다른지 확인
        assert thread_id_user1 != thread_id_user2, "각 사용자의 thread_id는 달라야 합니다"
        print("[OK] 각 사용자의 thread_id가 서로 다릅니다")
        
        print("\n" + "="*80)
        print("[OK] 모든 보안 테스트 통과!")
        print("="*80)
        
        print("\n[보안 검증 완료]")
        print("  - thread_id에 member_id 포함: OK")
        print("  - 같은 사용자의 thread 재사용: OK")
        print("  - 다른 사용자의 thread 접근 차단: OK")
        print("  - 각 사용자의 독립적인 대화: OK")
        
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] 검증 실패: {e}")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n[주의] 이 테스트는 다음 조건이 필요합니다:")
    print("  1. MySQL에 member_id=1, 2인 회원이 존재")
    print("  2. OPENAI_API_KEY가 .env에 설정되어 있음")
    print("\n진행하시겠습니까? (계속하려면 Enter, 취소하려면 Ctrl+C)")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n테스트 취소됨")
        sys.exit(0)
    
    success = test_thread_security()
    
    if not success:
        sys.exit(1)

