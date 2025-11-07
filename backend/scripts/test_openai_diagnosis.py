"""
OpenAI Vision API 기반 RAG 파이프라인 통합 테스트
- OpenAI Vision API로 이미지 진단 수행
- 진단 결과로 RAG 파이프라인 실행 (Vector 검색 + LLM 추천)
"""
import sys
import os
import re
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.config.database import SessionLocal
from app.services.recommendation import RecommendationService
from app.repository.member import MemberRepository
from app.repository.analysis import AnalysisRepository
from app.repository.diagnosis import DiagnosisRepository
from app.models.skin_analysis import SkinAnalysis
from app.utils.image import encode_image_base64
from app.utils.prompt import load_prompt
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# httpx HTTP 요청 로그 숨기기 (중복 제거)
logging.getLogger("httpx").setLevel(logging.WARNING)


def find_image_file(base_path: str, filename: str) -> str:
    """
    파일 확장자를 자동으로 찾아서 전체 경로 반환
    
    Args:
        base_path: 이미지가 있는 디렉토리 경로
        filename: 확장자 없는 파일명
        
    Returns:
        str: 전체 파일 경로
    """
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    for ext in extensions:
        full_path = os.path.join(base_path, filename + ext)
        if os.path.exists(full_path):
            return full_path
    
    raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {base_path}/{filename}.*")


def diagnose_with_openai(image_path: str) -> tuple[str, str]:
    """
    OpenAI Vision API로 피부 이미지 진단
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        tuple[str, str]: (disease_name, summary)
    """
    logger.info(f"이미지 로드: {image_path}")
    
    # 이미지 로드 및 Base64 인코딩
    image = Image.open(image_path).convert("RGB")
    image_base64 = encode_image_base64(image)
    logger.info(f"이미지 Base64 인코딩 완료 (길이: {len(image_base64)}자)")
    
    # 프롬프트 로드
    instruction = load_prompt("diagnosis.yaml")
    
    # OpenAI LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1,
    )
    
    # 메시지 구성
    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": instruction},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        )
    ]
    
    # OpenAI Vision API 호출
    logger.info("OpenAI Vision API 호출 시작...")
    response = llm.invoke(messages)
    logger.info("OpenAI Vision API 응답 수신 완료")
    
    # 결과 파싱
    disease_match = re.search(r"<label>(.*?)</label>", response.content)
    summary_match = re.search(r"<summary>(.*?)</summary>", response.content)
    
    if not disease_match or not summary_match:
        raise ValueError(f"AI 진단 응답 형식이 올바르지 않습니다.\n응답: {response.content}")
    
    disease_name = disease_match.group(1)
    summary = summary_match.group(1)
    
    logger.info(f"진단 완료: {disease_name}")
    
    return disease_name, summary


def main():
    print("=" * 80)
    print("OpenAI Vision API 기반 RAG 파이프라인 통합 테스트")
    print("=" * 80)
    
    # 테스트 이미지 설정
    image_base_path = r"C:\Users\201\Desktop\원천데이터\VS_여드름_정면"
    image_filename = "H2_2361_P3_L0"
    
    # 테스트 회원 ID
    member_id = 1
    
    # 테스트용 개인정보 (프론트의 메모리/상태 역할)
    test_skin_type = "건성"
    test_min_price = 1
    test_max_price = 500000
    
    # 테스트용 예시 - 1번회원: 건성, 1, 500000 / 2번회원: 지성, 1, 200000 / 3번회원: 건성, 15000, 100000

    db = SessionLocal()
    
    try:
        # 1. 회원 정보 확인
        member = MemberRepository.get_by_id(db, member_id)
        if not member:
            print("[ERROR] 회원 정보가 없습니다. init.sql을 먼저 실행하세요.")
            return
        
        print(f"\n[회원 정보]")
        print(f"   이름: {member.name}")
        print(f"   피부타입: {member.skin_type}")
        
        # 2. 이미지 파일 찾기
        print(f"\n[이미지 파일]")
        try:
            image_path = find_image_file(image_base_path, image_filename)
            print(f"   경로: {image_path}")
        except FileNotFoundError as e:
            print(f"[ERROR] {e}")
            return
        
        # 3. OpenAI Vision API로 진단
        print(f"\n[OpenAI Vision API로 피부 진단 중...]")
        try:
            disease_name, summary = diagnose_with_openai(image_path)
            
            print(f"\n[진단 완료!]")
            print(f"   질환: {disease_name}")
            # 상세 요약과 가공 내용은 아래 RAG 파이프라인 로그에서 출력됨
            
        except Exception as e:
            print(f"[ERROR] 진단 실패: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. 새 분석 레코드 생성 (실제 서비스와 동일)
        print(f"\n[MySQL에 분석 레코드 생성 중...]")
        analysis = AnalysisRepository.create(db, {
            "member_id": member_id,
            "skin_type": test_skin_type,
            "min_price": test_min_price,
            "max_price": test_max_price
        })
        db.flush()
        analysis_id = analysis.analysis_id
        print(f"   analysis_id: {analysis_id}")
        print(f"   피부타입: {analysis.skin_type}")
        print(f"   가격대: {analysis.min_price:,}원 ~ {analysis.max_price:,}원")
        
        # 5. DB에 진단 결과 저장
        diagnosis_data = {
            "analysis_id": analysis_id,
            "disease_name": disease_name,
            "summary": summary
        }
        diagnosis = DiagnosisRepository.create(db, diagnosis_data)
        db.commit()
        print(f"   diagnosis_id: {diagnosis.diagnosis_id}")
        
        # 6. RAG 파이프라인 실행
        print(f"\n[RAG 파이프라인 실행 중...]")
        print(f"   (Vector 검색 -> LLM 추천 -> MySQL 저장)")
        
        try:
            recommendations = RecommendationService.create_recommendations(
                db=db,
                analysis_id=analysis_id
            )
            
            print(f"\n[추천 완료! (총 {len(recommendations)}개)]")
            print(f"\n{'=' * 80}")
            print(f"추천 화장품 TOP {len(recommendations)}")
            print(f"{'=' * 80}")
            print(f"\n{'순위':<6} {'화장품명':<35} {'브랜드':<20} {'가격':<12}")
            print(f"-" * 80)
            
            for rec in recommendations:
                cosmetic = rec.cosmetic
                name = cosmetic.name[:33] + ".." if len(cosmetic.name) > 35 else cosmetic.name
                brand = cosmetic.brand[:18] + ".." if len(cosmetic.brand) > 20 else cosmetic.brand
                
                print(
                    f"{rec.ranking:<6} "
                    f"{name:<35} "
                    f"{brand:<20} "
                    f"{int(cosmetic.price):>10,}원"
                )
                print(f"       [추천 이유] {rec.reason}")
                print()
            
            print(f"[SUCCESS] MySQL recommendation 테이블 저장 완료")
            print(f"   recommendation_id: {[r.recommendation_id for r in recommendations]}")
            print(f"   cosmetic_id: {[r.cosmetic_id for r in recommendations]}")
            
        except Exception as e:
            print(f"[ERROR] RAG 파이프라인 실행 실패: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"\n" + "=" * 80)
        print(f"[테스트 완료!]")
        print(f"=" * 80)
        print(f"\n[결과 요약]")
        print(f"   - analysis_id: {analysis_id}")
        print(f"   - 진단: {disease_name}")
        print(f"   - 추천 제품 수: {len(recommendations)}개")
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

