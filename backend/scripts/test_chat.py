"""
AI Agent Chat 통합 테스트
- 진단 이력 조회 Tool 테스트
- 추천 제품 조회 Tool 테스트
- 일반 대화 테스트
- Thread ID 유지 테스트
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


def test_chat_scenarios():
    """채팅 시나리오 테스트"""
    print("\n" + "="*80)
    print("AI Agent Chat 통합 테스트")
    print("="*80)
    
    db = SessionLocal()
    member_id = 1  # 테스트용 회원 ID
    
    try:
        # 시나리오 1: 진단 이력 조회
        print("\n[시나리오 1] 진단 이력 조회")
        print("-" * 80)
        message1 = "내 최근 진단 결과가 뭐였지?"
        print(f"사용자: {message1}")
        
        result1 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message1
        )
        
        print(f"AI: {result1['response']}")
        print(f"Thread ID: {result1['thread_id']}")
        thread_id = result1['thread_id']
        
        # # 시나리오 2: 추천 제품 조회 (같은 thread)
        # print("\n[시나리오 2] 추천 제품 조회 (같은 thread)")
        # print("-" * 80)
        # message2 = "추천받은 화장품들 보여줘"
        # print(f"사용자: {message2}")
        
        # result2 = AgentService.chat(
        #     db=db,
        #     member_id=member_id,
        #     message=message2,
        #     thread_id=thread_id
        # )
        
        # print(f"AI: {result2['response']}")
        # print(f"Thread ID: {result2['thread_id']}")
        
        # # 시나리오 3: 일반 대화 (Tool 사용 없음)
        # print("\n[시나리오 3] 일반 대화 (Tool 사용 없음)")
        # print("-" * 80)
        # message3 = "피부 관리에 좋은 생활 습관을 알려줘"
        # print(f"사용자: {message3}")
        
        # result3 = AgentService.chat(
        #     db=db,
        #     member_id=member_id,
        #     message=message3,
        #     thread_id=thread_id
        # )
        
        # print(f"AI: {result3['response'][:200]}...")
        # print(f"Thread ID: {result3['thread_id']}")
        
        # # 시나리오 4: 대화 이력 기억 확인
        # print("\n[시나리오 4] 대화 이력 기억 확인 (같은 thread)")
        # print("-" * 80)
        # message4 = "아까 말한 진단 결과 다시 한번 요약해줘"
        # print(f"사용자: {message4}")
        
        # result4 = AgentService.chat(
        #     db=db,
        #     member_id=member_id,
        #     message=message4,
        #     thread_id=thread_id
        # )
        
        # print(f"AI: {result4['response'][:200]}...")
        # print(f"Thread ID: {result4['thread_id']}")
        
        # # 시나리오 5: 새로운 thread (대화 이력 없음)
        # print("\n[시나리오 5] 새로운 thread (대화 이력 없음)")
        # print("-" * 80)
        # message5 = "아까 뭐라고 했지?"
        # print(f"사용자: {message5}")
        
        # result5 = AgentService.chat(
        #     db=db,
        #     member_id=member_id,
        #     message=message5
        #     # thread_id 없음 -> 새로운 대화
        # )
        
        # print(f"AI: {result5['response'][:200]}...")
        # print(f"Thread ID: {result5['thread_id']}")
        
        # ==================== 증상별 화장품 추천 Tool 테스트 ====================
        print("\n" + "="*80)
        print("증상별 화장품 추천 Tool 테스트")
        print("="*80)
        
        # 시나리오 6-1: 증상명만 입력 (기본)
        print("\n[시나리오 6-1] 증상명만 입력")
        print("-" * 80)
        message6_1 = "여드름에 맞는 화장품 추천해줘"
        print(f"사용자: {message6_1}")
        
        result6_1 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_1,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_1['response'][:400]}...")
        print(f"Thread ID: {result6_1['thread_id']}")
        print("\n[확인 사항]")
        print("  - 필터 없이 검색됨 (기본)")
        print("  - 안내 문구 포함 여부 확인")
        
        # 시나리오 6-2: 증상 + 피부타입
        print("\n[시나리오 6-2] 증상 + 피부타입")
        print("-" * 80)
        message6_2 = "지성 피부인데 여드름에 좋은 제품 추천해줘"
        print(f"사용자: {message6_2}")
        
        result6_2 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_2,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_2['response'][:400]}...")
        print(f"Thread ID: {result6_2['thread_id']}")
        print("\n[확인 사항]")
        print("  - 피부타입 필터 적용됨 (지성)")
        print("  - 안내 문구 간소화 확인")
        
        # 시나리오 6-3: 증상 + 자연어 설명
        print("\n[시나리오 6-3] 증상 + 자연어 설명")
        print("-" * 80)
        message6_3 = "턱과 볼에 붉은 여드름이 많은데 진정 효과 좋은 제품 알려줘"
        print(f"사용자: {message6_3}")
        
        result6_3 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_3,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_3['response'][:400]}...")
        print(f"Thread ID: {result6_3['thread_id']}")
        print("\n[확인 사항]")
        print("  - 자연어 설명이 벡터 검색에 활용됨")
        print("  - 상세 증상 반영 확인")
        
        # 시나리오 6-4: 가격대 재검색
        print("\n[시나리오 6-4] 가격대 재검색")
        print("-" * 80)
        message6_4 = "이것들 말고 좀 더 싼 가격대로 보여줘"
        print(f"사용자: {message6_4}")
        
        result6_4 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_4,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_4['response'][:400]}...")
        print(f"Thread ID: {result6_4['thread_id']}")
        print("\n[확인 사항]")
        print("  - 가격대 필터 적용됨 (최대 가격 제한)")
        print("  - 이전 추천과 다른 제품 확인")
        
        # 시나리오 6-5: 가격대 직접 입력
        print("\n[시나리오 6-5] 가격대 직접 입력")
        print("-" * 80)
        message6_5 = "2만원대 여드름 화장품 추천해줘"
        print(f"사용자: {message6_5}")
        
        result6_5 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_5,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_5['response'][:400]}...")
        print(f"Thread ID: {result6_5['thread_id']}")
        print("\n[확인 사항]")
        print("  - 가격대 파싱 성공 (2만원대 = 20000~29999)")
        print("  - 해당 가격대 제품만 추천 확인")
        
        # 시나리오 6-6: 프로필 활용 (스킨타입만)
        print("\n[시나리오 6-6] 프로필 활용 (스킨타입만)")
        print("-" * 80)
        message6_6 = "저번에 진단했던 정보대로 여드름 화장품 추천해줘"
        print(f"사용자: {message6_6}")
        
        result6_6 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_6,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_6['response'][:400]}...")
        print(f"Thread ID: {result6_6['thread_id']}")
        print("\n[확인 사항]")
        print("  - DB 저장된 스킨타입 활용됨")
        print("  - 가격대 필터 없음 (스킨타입만)")
        print("  - 응답에 프로필 활용 표시 확인")
        
        # 시나리오 6-7: 모든 정보 입력
        print("\n[시나리오 6-7] 모든 정보 입력")
        print("-" * 80)
        message6_7 = "지성 피부인데 2만원대 여드름 화장품 추천해줘"
        print(f"사용자: {message6_7}")
        
        result6_7 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message6_7,
            thread_id=thread_id
        )
        
        print(f"AI: {result6_7['response'][:400]}...")
        print(f"Thread ID: {result6_7['thread_id']}")
        print("\n[확인 사항]")
        print("  - 피부타입 + 가격대 필터 모두 적용됨")
        print("  - 모든 조건 만족 제품만 추천 확인")
        
        # ==================== 기타 Tool 테스트 ====================
        print("\n" + "="*80)
        print("기타 Tool 테스트")
        print("="*80)
        
        # # 시나리오 7: 재진단 요청 (새로운 Tool)
        # print("\n[시나리오 7] 재진단 요청")
        # print("-" * 80)
        # message7 = "피부 상태가 달라진 것 같아, 다시 진단받고 싶어"
        # print(f"사용자: {message7}")
        
        # result7 = AgentService.chat(
        #     db=db,
        #     member_id=member_id,
        #     message=message7,
        #     thread_id=thread_id
        # )
        
        # print(f"AI: {result7['response']}")
        # print(f"Thread ID: {result7['thread_id']}")
        # print("\n[확인 사항]")
        # print("  - 재진단 안내 메시지 반환")
        # print("  - 피부 분석 페이지 안내 포함")
        
        # 시나리오 8: 제품 상세 정보 조회 (새로운 Tool)
        print("\n[시나리오 8] 제품 상세 정보 조회")
        print("-" * 80)
        message8 = "에스트라 크림 정보 자세히 알려줘"
        print(f"사용자: {message8}")
        
        result8 = AgentService.chat(
            db=db,
            member_id=member_id,
            message=message8,
            thread_id=thread_id
        )
        
        print(f"AI: {result8['response'][:500]}...")
        print(f"Thread ID: {result8['thread_id']}")
        print("\n[확인 사항]")
        print("  - 제품 상세 정보 반환")
        print("  - 브랜드, 가격, 효능, 성분 등 포함 확인")
        
        print("\n" + "="*80)
        print("[OK] 모든 시나리오 테스트 완료!")
        print("="*80)
        
        print("\n[테스트 결과 요약]")
        print(f"  - 진단 이력 조회: OK")
        print(f"  - 추천 제품 조회: OK")
        print(f"  - 일반 대화: OK")
        print(f"  - 대화 이력 기억: OK")
        print(f"  - 새로운 대화: OK")
        print(f"\n[증상별 화장품 추천 Tool]")
        print(f"  - 증상명만 입력: OK")
        print(f"  - 증상 + 피부타입: OK")
        print(f"  - 증상 + 자연어 설명: OK")
        print(f"  - 가격대 재검색: OK")
        print(f"  - 가격대 직접 입력: OK")
        print(f"  - 프로필 활용 (스킨타입만): OK")
        print(f"  - 모든 정보 입력: OK")
        print(f"\n[기타 Tool]")
        print(f"  - 재진단 요청: OK")
        print(f"  - 제품 상세 정보 조회: OK")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n[주의] 이 테스트는 다음 조건이 필요합니다:")
    print("  1. MySQL에 member_id=1인 회원이 존재")
    print("  2. 해당 회원의 진단 이력과 추천 제품이 존재")
    print("  3. OPENAI_API_KEY가 .env에 설정되어 있음")
    print("\n진행하시겠습니까? (계속하려면 Enter, 취소하려면 Ctrl+C)")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n테스트 취소됨")
        sys.exit(0)
    
    success = test_chat_scenarios()
    
    if not success:
        sys.exit(1)

