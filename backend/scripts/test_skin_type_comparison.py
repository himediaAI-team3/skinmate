"""
피부타입별 추천 비교 테스트
- 같은 이미지와 진단 결과를 사용하여 피부타입만 다르게(건성/지성) 테스트
- 추천 결과 비교 분석
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
    (한 번만 실행하여 결과 재사용)
    
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


def test_with_skin_type(
    db,
    member_id: int,
    skin_type: str,
    disease_name: str,
    summary: str
) -> list:
    """
    특정 피부타입으로 추천 테스트
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        skin_type: 테스트할 피부타입 ("건성" 또는 "지성")
        disease_name: 진단된 질환명
        summary: 진단 요약
        
    Returns:
        list: Recommendation 객체 리스트
    """
    print(f"\n{'=' * 80}")
    print(f"[피부타입: {skin_type} 테스트 시작]")
    print(f"{'=' * 80}")
    
    # 1. 회원 정보 조회 및 피부타입 저장
    member = MemberRepository.get_by_id(db, member_id)
    if not member:
        raise ValueError(f"회원 정보를 찾을 수 없습니다: member_id={member_id}")
    
    original_skin_type = member.skin_type
    print(f"\n[회원 정보]")
    print(f"   원래 피부타입: {original_skin_type}")
    
    # 2. 피부타입 임시 업데이트
    MemberRepository.update(db, member_id, {"skin_type": skin_type})
    db.commit()
    
    # 업데이트된 회원 정보 확인
    member = MemberRepository.get_by_id(db, member_id)
    print(f"   변경된 피부타입: {member.skin_type}")
    print(f"   가격대: {member.min_price:,}원 ~ {member.max_price:,}원")
    
    # 3. 새로운 analysis 레코드 생성
    print(f"\n[MySQL에 분석 레코드 생성 중...]")
    analysis = AnalysisRepository.create(db, {"member_id": member_id})
    db.flush()
    analysis_id = analysis.analysis_id
    print(f"   analysis_id: {analysis_id}")
    
    # 4. 동일한 diagnosis 결과 저장
    print(f"\n[진단 결과 저장 중...]")
    diagnosis_data = {
        "analysis_id": analysis_id,
        "disease_name": disease_name,
        "summary": summary
    }
    diagnosis = DiagnosisRepository.create(db, diagnosis_data)
    db.commit()
    print(f"   diagnosis_id: {diagnosis.diagnosis_id}")
    print(f"   질환: {disease_name}")
    
    # 5. RAG 파이프라인 실행
    print(f"\n[RAG 파이프라인 실행 중...]")
    print(f"   (Vector 검색 -> LLM 추천 -> MySQL 저장)")
    
    try:
        recommendations = RecommendationService.create_recommendations(
            db=db,
            analysis_id=analysis_id,
            member_id=member_id
        )
        
        print(f"\n[추천 완료! (총 {len(recommendations)}개)]")
        print(f"\n{'=' * 80}")
        print(f"피부타입 '{skin_type}' 추천 화장품 TOP {len(recommendations)}")
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
        
        return recommendations
        
    except Exception as e:
        print(f"[ERROR] RAG 파이프라인 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        raise


def compare_recommendations(dry_recs: list, oily_recs: list):
    """
    건성과 지성 피부타입의 추천 결과 비교
    
    Args:
        dry_recs: 건성 피부 추천 결과 리스트
        oily_recs: 지성 피부 추천 결과 리스트
    """
    print(f"\n\n{'=' * 80}")
    print(f"[추천 결과 비교 분석]")
    print(f"{'=' * 80}")
    
    # 추천된 화장품 ID 추출
    dry_cosmetic_ids = {rec.cosmetic_id: rec for rec in dry_recs}
    oily_cosmetic_ids = {rec.cosmetic_id: rec for rec in oily_recs}
    
    # 공통 제품과 차이점 분석
    common_ids = set(dry_cosmetic_ids.keys()) & set(oily_cosmetic_ids.keys())
    dry_only_ids = set(dry_cosmetic_ids.keys()) - set(oily_cosmetic_ids.keys())
    oily_only_ids = set(oily_cosmetic_ids.keys()) - set(dry_cosmetic_ids.keys())
    
    print(f"\n[공통 추천 제품] (총 {len(common_ids)}개)")
    if common_ids:
        print(f"\n{'순위(건성)':<12} {'순위(지성)':<12} {'화장품명':<35} {'브랜드':<20}")
        print(f"-" * 80)
        for cosmetic_id in sorted(common_ids):
            dry_rec = dry_cosmetic_ids[cosmetic_id]
            oily_rec = oily_cosmetic_ids[cosmetic_id]
            cosmetic = dry_rec.cosmetic
            name = cosmetic.name[:33] + ".." if len(cosmetic.name) > 35 else cosmetic.name
            brand = cosmetic.brand[:18] + ".." if len(cosmetic.brand) > 20 else cosmetic.brand
            
            print(f"{dry_rec.ranking:<12} {oily_rec.ranking:<12} {name:<35} {brand:<20}")
    else:
        print("   공통 추천 제품이 없습니다.")
    
    print(f"\n[건성 피부만 추천된 제품] (총 {len(dry_only_ids)}개)")
    if dry_only_ids:
        print(f"\n{'순위':<6} {'화장품명':<35} {'브랜드':<20} {'가격':<12}")
        print(f"-" * 80)
        for cosmetic_id in sorted(dry_only_ids, key=lambda x: dry_cosmetic_ids[x].ranking):
            rec = dry_cosmetic_ids[cosmetic_id]
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
    else:
        print("   없음")
    
    print(f"\n[지성 피부만 추천된 제품] (총 {len(oily_only_ids)}개)")
    if oily_only_ids:
        print(f"\n{'순위':<6} {'화장품명':<35} {'브랜드':<20} {'가격':<12}")
        print(f"-" * 80)
        for cosmetic_id in sorted(oily_only_ids, key=lambda x: oily_cosmetic_ids[x].ranking):
            rec = oily_cosmetic_ids[cosmetic_id]
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
    else:
        print("   없음")
    
    # 통계 요약
    print(f"\n[비교 요약]")
    print(f"   공통 추천 제품: {len(common_ids)}개")
    print(f"   건성만 추천: {len(dry_only_ids)}개")
    print(f"   지성만 추천: {len(oily_only_ids)}개")
    print(f"   전체 추천 제품 수: {len(dry_cosmetic_ids | oily_cosmetic_ids)}개")


def main():
    print("=" * 80)
    print("피부타입별 추천 비교 테스트")
    print("=" * 80)
    
    # 테스트 이미지 설정
    image_base_path = r"C:\Users\201\Desktop\원천데이터\VS_여드름_정면"
    image_filename = "H2_2361_P3_L0"
    member_id = 1
    
    db = SessionLocal()
    
    original_skin_type = None
    
    try:
        # 1. 회원 정보 확인
        member = MemberRepository.get_by_id(db, member_id)
        if not member:
            print("[ERROR] 회원 정보가 없습니다. init.sql을 먼저 실행하세요.")
            return
        
        # 원래 피부타입 저장 (나중에 복구용)
        original_skin_type = member.skin_type
        
        print(f"\n[회원 정보]")
        print(f"   이름: {member.name}")
        print(f"   현재 피부타입: {member.skin_type}")
        print(f"   가격대: {member.min_price:,}원 ~ {member.max_price:,}원")
        
        # 2. 이미지 파일 찾기
        print(f"\n[이미지 파일]")
        try:
            image_path = find_image_file(image_base_path, image_filename)
            print(f"   경로: {image_path}")
        except FileNotFoundError as e:
            print(f"[ERROR] {e}")
            return
        
        # 3. OpenAI Vision API로 진단 (한 번만 실행)
        print(f"\n[OpenAI Vision API로 피부 진단 중...]")
        try:
            disease_name, summary = diagnose_with_openai(image_path)
            
            print(f"\n[진단 완료!]")
            print(f"   질환: {disease_name}")
            print(f"   요약: {summary[:100]}...")
            
        except Exception as e:
            print(f"[ERROR] 진단 실패: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. 피부타입별로 테스트
        skin_types = ["건성", "지성"]
        all_recommendations = {}
        
        for skin_type in skin_types:
            try:
                recommendations = test_with_skin_type(
                    db=db,
                    member_id=member_id,
                    skin_type=skin_type,
                    disease_name=disease_name,
                    summary=summary
                )
                all_recommendations[skin_type] = recommendations
                
            except Exception as e:
                print(f"[ERROR] 피부타입 '{skin_type}' 테스트 실패: {e}")
                import traceback
                traceback.print_exc()
                # 계속 진행 (다른 피부타입 테스트)
        
        # 5. 결과 비교
        if len(all_recommendations) == 2:
            dry_recs = all_recommendations["건성"]
            oily_recs = all_recommendations["지성"]
            compare_recommendations(dry_recs, oily_recs)
        else:
            print(f"\n[WARNING] 두 피부타입 모두 테스트 완료되지 않아 비교를 생략합니다.")
        
        # 6. 원래 피부타입으로 복구
        if original_skin_type:
            print(f"\n[피부타입 복구 중...]")
            MemberRepository.update(db, member_id, {"skin_type": original_skin_type})
            db.commit()
            print(f"   피부타입이 원래 값 '{original_skin_type}'으로 복구되었습니다.")
        
        print(f"\n" + "=" * 80)
        print(f"[테스트 완료!]")
        print(f"=" * 80)
        print(f"\n[결과 요약]")
        print(f"   - 진단 질환: {disease_name}")
        for skin_type, recs in all_recommendations.items():
            print(f"   - {skin_type} 피부 추천 제품 수: {len(recs)}개")
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

