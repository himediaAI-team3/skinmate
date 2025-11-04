"""
AI Agent용 Tool 정의
- 사용자의 진단 이력 조회
- 추천 제품 조회
"""
from langchain.tools import tool
from sqlalchemy.orm import Session
from app.core.config.database import SessionLocal
from app.repository.diagnosis import DiagnosisRepository
from app.repository.analysis import AnalysisRepository
from app.repository.recommendation import RecommendationRepository
from app.repository.cosmetic import CosmeticRepository
from app.repository.member import MemberRepository
from app.services.vector_store import VectorStoreService
from app.services.recommendation import RecommendationService
from app.models.cosmetic import Cosmetic
from typing import Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


@tool
def get_my_diagnosis_history() -> Dict[str, Any]:
    """사용자의 최근 피부 진단 이력을 조회합니다.
    
    Returns:
        dict: 최근 진단 정보 (진단명, 날짜, 요약)
    """
    # Tool 실행 시 runtime에서 user_id를 가져올 수 있도록
    # 실제로는 agent.invoke 시 전달된 state에서 가져옴
    # 여기서는 임시로 구조만 작성
    logger.info("[Tool] get_my_diagnosis_history 호출")
    
    # 주의: runtime.state는 실제 Agent 실행 시에만 접근 가능
    # 여기서는 함수 시그니처만 정의하고, 실제 구현은 wrapper에서 처리
    return {
        "error": "이 Tool은 Agent context에서만 실행 가능합니다."
    }


@tool
def get_recommended_products() -> Dict[str, Any]:
    """최근 추천받은 화장품 3개를 조회합니다.
    
    Returns:
        dict: 추천 제품 목록
    """
    logger.info("[Tool] get_recommended_products 호출")
    
    return {
        "error": "이 Tool은 Agent context에서만 실행 가능합니다."
    }


# ==================== Runtime state 접근 가능한 Wrapper 함수 ====================
def create_diagnosis_history_tool(db: Session, member_id: int):
    """
    member_id를 closure로 캡처한 진단 이력 조회 Tool 생성
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        tool: 실행 가능한 Tool 함수
    """
    @tool
    def get_my_diagnosis_history_impl() -> str:
        """사용자의 최근 피부 진단 이력을 조회합니다."""
        try:
            # 1. 최근 분석 이력 조회 (1개만)
            history = AnalysisRepository.get_by_member_id_with_pagination(
                db, member_id, page=1, size=1
            )
            
            if not history:
                return "아직 진단 이력이 없습니다. 첫 피부 분석을 진행해보세요!"
            
            analysis = history[0]
            
            # 2. 진단 정보 조회
            diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis.analysis_id)
            
            if not diagnosis:
                return f"분석 기록은 있지만 진단 정보가 없습니다. (분석 ID: {analysis.analysis_id})"
            
            # 3. 결과 포맷팅
            result = f"""**최근 진단 결과**
- 진단일: {analysis.created_at.strftime('%Y년 %m월 %d일')}
- 진단명: {diagnosis.disease_name}
- 증상 요약: {diagnosis.summary[:100]}{'...' if len(diagnosis.summary) > 100 else ''}
"""
            return result
            
        except Exception as e:
            logger.error(f"진단 이력 조회 실패: {e}")
            return f"진단 이력 조회 중 오류가 발생했습니다: {str(e)}"
    
    return get_my_diagnosis_history_impl


def create_recommended_products_tool(db: Session, member_id: int):
    """
    member_id를 closure로 캡처한 추천 제품 조회 Tool 생성
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        tool: 실행 가능한 Tool 함수
    """
    @tool
    def get_recommended_products_impl() -> str:
        """최근 추천받은 화장품 3개를 조회합니다."""
        try:
            # 1. 최근 분석 이력 조회
            history = AnalysisRepository.get_by_member_id_with_pagination(
                db, member_id, page=1, size=1
            )
            
            if not history:
                return "아직 추천 제품이 없습니다. 먼저 피부 분석을 진행해주세요!"
            
            analysis = history[0]
            
            # 2. 추천 제품 조회 (ranking 순)
            recommendations = RecommendationRepository.get_by_analysis_id(
                db, analysis.analysis_id
            )
            
            if not recommendations:
                return "추천 제품이 없습니다."
            
            # 3. 화장품 상세 정보 조회
            cosmetic_ids = [r.cosmetic_id for r in recommendations]
            cosmetics = CosmeticRepository.get_by_ids(db, cosmetic_ids)
            cosmetic_dict = {c.cosmetic_id: c for c in cosmetics}
            
            # 4. 결과 포맷팅
            result = "**추천 화장품 목록**\n\n"
            for rec in recommendations:
                cosmetic = cosmetic_dict.get(rec.cosmetic_id)
                if cosmetic:
                    result += f"{rec.ranking}. {cosmetic.name} ({cosmetic.brand})\n"
                    result += f"   - 가격: {int(cosmetic.price):,}원\n"
                    result += f"   - 추천 이유: {rec.reason}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"추천 제품 조회 실패: {e}")
            return f"추천 제품 조회 중 오류가 발생했습니다: {str(e)}"
    
    return get_recommended_products_impl


def parse_price_range(price_range: str) -> tuple:
    """가격대 문자열을 (min_price, max_price)로 변환
    
    Args:
        price_range: 가격대 문자열 (예: "2만원대", "3-5만원", "5만원 이상")
        
    Returns:
        tuple: (min_price, max_price) 또는 (None, None)
    """
    if not price_range:
        return (None, None)
    
    # "2만원대" → 20000~29999
    if "만원대" in price_range:
        match = re.search(r'(\d+)만원대', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (base, base + 9999)
    
    # "3-5만원" 또는 "3~5만원" → 30000~50000
    elif "~" in price_range or "-" in price_range:
        parts = re.findall(r'(\d+)', price_range)
        if len(parts) >= 2:
            return (int(parts[0]) * 10000, int(parts[1]) * 10000)
    
    # "5만원 이상" → 50000 이상
    elif "이상" in price_range:
        match = re.search(r'(\d+)만원', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (base, 999999)
    
    # "5만원 이하" → 5만원 이하
    elif "이하" in price_range:
        match = re.search(r'(\d+)만원', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (0, base)
    
    return (None, None)


def create_recommend_by_symptom_tool(db: Session, member_id: int):
    """증상별 화장품 재추천 Tool 생성"""
    
    @tool
    def recommend_by_symptom_impl(
        symptom: str,
        skin_type: str = None,
        detail: str = None,
        use_my_profile: bool = False,
        min_price: int = None,
        max_price: int = None,
        price_range: str = None
    ) -> str:
        """특정 증상에 맞는 화장품을 추천합니다.
        
        Args:
            symptom: 피부 증상 (필수) - 예: "여드름", "아토피", "건선", "주사", "지루"
            skin_type: 피부 타입 (선택) - 예: "지성", "건성", "복합성", "민감성"
            detail: 상세 증상 설명 (선택) - 예: "볼과 턱에 붉은 여드름이 많음, 진정 효과 필요"
            use_my_profile: 내 회원 정보 활용 여부 (선택) - True면 DB 저장된 스킨타입만 활용 (가격대 제외)
            min_price: 최소 가격 (선택) - 단위: 원
            max_price: 최대 가격 (선택) - 단위: 원
            price_range: 가격대 범위 (선택) - 예: "2만원대", "3-5만원", "5만원 이상"
        """
        try:
            # 1. 필터 구성
            filters = {"skin_disease": symptom}
            query_parts = [symptom]
            
            # 2. 프로필 활용 (스킨타입만)
            if use_my_profile:
                member = MemberRepository.get_by_id(db, member_id)
                if member and member.skin_type:
                    filters["skin_type"] = member.skin_type
                    query_parts.append(member.skin_type)
            
            # 3. 사용자 입력 정보
            if skin_type:
                filters["skin_type"] = skin_type  # 덮어쓰기
                if skin_type not in query_parts:
                    query_parts.append(skin_type)
            
            if detail:
                query_parts.append(detail)
            
            # 4. 가격대 처리
            if price_range:
                parsed_min, parsed_max = parse_price_range(price_range)
                if parsed_min is not None and parsed_max is not None:
                    filters["price_range"] = [parsed_min, parsed_max]
            elif min_price is not None or max_price is not None:
                filters["price_range"] = [
                    min_price or 0,
                    max_price or 999999
                ]
            
            # 5. 벡터 검색 - LLM으로 쿼리 변환 후 기존 search_hybrid() 호출
            from app.utils.prompt import load_prompt
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            import json
            import os
            
            # 자연어 쿼리 생성
            query = " ".join(query_parts) + " 케어"
            
            # LLM으로 dense/sparse 쿼리 변환
            instruction = load_prompt("summary_refine_chat.yaml")
            filled = instruction.format(
                disease_name=symptom,
                summary=query
            )
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1,
            )
            
            resp = llm.invoke([HumanMessage(content=filled)])
            
            # JSON 파싱
            content = resp.content.strip()
            if content.startswith("```"):
                content = content.strip("`").strip("json").strip()
            
            query_data = json.loads(content)
            
            logger.info(f"검색 쿼리 생성 완료: dense={query_data['dense_query'][:50]}...")
            logger.info(f"검색 쿼리 생성 완료: sparse={query_data['sparse_keywords'][:80]}...")
            
            # 가격대 추출
            price_range_val = filters.get("price_range")
            min_price_val = None
            max_price_val = None
            if price_range_val:
                min_price_val = price_range_val[0]
                max_price_val = price_range_val[1]
            
            # 기존 search_hybrid() 메서드 호출
            search_results = VectorStoreService.search_hybrid(
                query_dense_text=query_data["dense_query"],
                query_sparse_text=query_data["sparse_keywords"],
                min_price=min_price_val,
                max_price=max_price_val,
                skin_type=filters.get("skin_type"),
                disease_name=symptom,
                limit=10
            )
            
            if len(search_results) == 0:
                return f"'{symptom}' 증상에 적합한 화장품을 찾을 수 없습니다. 다른 조건으로 검색해보세요."
            
            # 6. MySQL에서 상세 정보 조회 (예외 시 롤백)
            cosmetic_ids = [r['cosmetic_id'] for r in search_results]
            try:
                cosmetics = CosmeticRepository.get_by_ids(db, cosmetic_ids)
            except Exception as e:
                try:
                    db.rollback()
                except Exception:
                    pass
                logger.error("DB 조회 실패(get_by_ids)", exc_info=True)
                return "시스템 오류로 추천을 완료하지 못했습니다. 잠시 후 다시 시도해주세요."
            
            # 7. LLM으로 최종 3개 선정 (기존 로직 재사용)
            search_scores = {r['cosmetic_id']: r['score'] for r in search_results}
            
            # 가상 진단 객체 생성 (LLM 호출용) - 사용자 입력 정보 포함
            class FakeDiagnosis:
                def __init__(self, disease_name, summary):
                    self.disease_name = disease_name
                    self.summary = summary
            
            # summary 구성: 피부 타입, 상세 설명 등 사용자 입력 정보 반영
            summary_parts = []
            if skin_type:
                summary_parts.append(f"{skin_type} 피부")
            if detail:
                summary_parts.append(detail)
            if not summary_parts:
                summary_parts.append(f"{symptom} 증상 케어")
            
            diagnosis_summary = ", ".join(summary_parts) if summary_parts else f"{symptom} 증상 케어"
            
            diagnosis = FakeDiagnosis(
                disease_name=symptom,
                summary=diagnosis_summary
            )
            
            # 회원 정보 조회 (LLM 선정용)
            member = MemberRepository.get_by_id(db, member_id)
            
            # 사용자 입력 정보가 있으면 임시 member 객체 생성 (원본 member는 변경하지 않음)
            if skin_type and member:
                class TempMember:
                    def __init__(self, original_member, temp_skin_type):
                        # 원본 member의 모든 속성 복사
                        for attr in dir(original_member):
                            if not attr.startswith('_'):
                                try:
                                    setattr(self, attr, getattr(original_member, attr))
                                except:
                                    pass
                        # skin_type만 사용자 입력값으로 변경
                        self.skin_type = temp_skin_type
                
                member = TempMember(member, skin_type)
            
            final_recommendations = RecommendationService._select_top3_with_llm(
                diagnosis=diagnosis,
                cosmetics=cosmetics,
                search_scores=search_scores,
                member=member
            )
            
            # 8. 결과 포맷팅
            result = f"**{symptom} 증상에 적합한 화장품 TOP 3**\n\n"
            
            for rec in final_recommendations:
                cosmetic = next((c for c in cosmetics if c.cosmetic_id == rec['cosmetic_id']), None)
                if cosmetic:
                    result += f"{rec['ranking']}. {cosmetic.name} ({cosmetic.brand})\n"
                    result += f"   - 가격: {int(cosmetic.price):,}원\n"
                    result += f"   - 추천 이유: {rec['reason']}\n\n"
            
            # 안내 문구 추가
            has_filter = bool(skin_type or filters.get("price_range") or use_my_profile)
            if not has_filter:
                result += "💡 **더 정확한 추천을 원하시나요?**\n"
                result += "- 피부 타입을 알려주시면 더 적합한 제품을 추천해드려요\n"
                result += "- 가격대를 지정해주시면 원하는 가격대의 제품을 찾아드려요 (예: \"2만원대로\", \"3-5만원\")\n"
                result += "- 증상을 구체적으로 설명해주시면 맞춤 추천이 가능합니다\n"
                result += "- 이전 진단 정보를 활용하려면 \"내 피부 타입으로 추천해줘\"라고 말씀해주세요\n"
            elif not filters.get("price_range"):
                result += "💡 가격대를 지정해주시면 원하는 가격대의 제품을 찾아드려요 (예: \"2만원대로\", \"3-5만원\")\n"
            
            return result
            
        except Exception as e:
            logger.error(f"증상별 추천 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"화장품 추천 중 오류가 발생했습니다: {str(e)}"
    
    return recommend_by_symptom_impl


def create_request_rediagnosis_tool():
    """재진단 요청 안내 Tool 생성"""
    
    @tool
    def request_rediagnosis_impl() -> str:
        """재진단을 요청합니다. 새로운 얼굴 사진 업로드 페이지로 안내합니다."""
        return """
🔄 재진단을 원하시는군요!

피부 상태는 계속 변화하므로 정기적인 진단이 중요합니다.

**다음 단계:**
1. 앱에서 '피부 분석' 메뉴로 이동
2. 새로운 얼굴 사진 촬영
3. AI 진단 결과 확인

📱 피부 분석 페이지로 이동해주세요!

💡 **재진단이 필요한 경우:**
- 피부 상태가 변화했을 때
- 새로운 증상이 나타났을 때
- 약 2-4주 주기로 권장
"""
    
    return request_rediagnosis_impl


def create_get_product_detail_tool(db: Session, member_id: int):
    """제품 상세 정보 조회 Tool 생성"""
    
    @tool
    def get_product_detail_impl(product_name: str) -> str:
        """특정 화장품의 상세 정보를 조회합니다.
        
        Args:
            product_name: 화장품 이름 (예: "아이디플라코스메틱 엑소브이 플러스 앰플")
        """
        try:
            # 1. 입력 파싱 & 정규화: 브랜드, 카테고리, 이름 키워드 추출
            def normalize_text(text: str) -> str:
                return " ".join(text.strip().split())

            CATEGORY_SYNONYMS = {
                "크림": ["크림", "모이스처라이저", "cream", "moisturizer"],
                "세럼": ["세럼", "에센스", "앰플", "serum", "essence", "ampoule"],
                "토너": ["토너", "스킨", "toner", "skin"],
            }

            def map_category(token: str) -> str | None:
                for canon, syns in CATEGORY_SYNONYMS.items():
                    if token.lower() in [s.lower() for s in syns]:
                        return canon
                return None

            normalized = normalize_text(product_name)
            tokens = normalized.split()

            brand_tokens: list[str] = []
            name_tokens: list[str] = []
            category_token: str | None = None

            for idx, token in enumerate(tokens):
                cat = map_category(token)
                if cat and not category_token:
                    category_token = cat
                    continue
                if idx == 0 and len(tokens) > 1 and not brand_tokens:
                    brand_tokens.append(token)
                else:
                    name_tokens.append(token)
            
            # 2. DB에서 정확 매칭 (브랜드 AND (카테고리 OR 제품명))
            try:
                from sqlalchemy import and_, or_
                query = db.query(Cosmetic)

                filters_and = []
                # 브랜드: OR(여러 토큰) → AND에 포함
                if brand_tokens:
                    brand_or = None
                    for bt in brand_tokens:
                        brand_or = (Cosmetic.brand.like(f"%{bt}%")) if brand_or is None else (
                            brand_or | Cosmetic.brand.like(f"%{bt}%")
                        )
                    if brand_or is not None:
                        filters_and.append(brand_or)

                # (카테고리 OR 이름): OR 묶음 → AND에 포함
                category_or = None
                if category_token:
                    category_or = Cosmetic.category.like(f"%{category_token}%") | Cosmetic.name.like(f"%{category_token}%")

                name_or = None
                if name_tokens:
                    for nt in name_tokens:
                        name_or = (Cosmetic.name.like(f"%{nt}%")) if name_or is None else (
                            name_or | Cosmetic.name.like(f"%{nt}%")
                        )

                cat_or_name = None
                if category_or is not None and name_or is not None:
                    cat_or_name = category_or | name_or
                elif category_or is not None:
                    cat_or_name = category_or
                elif name_or is not None:
                    cat_or_name = name_or

                if cat_or_name is not None:
                    filters_and.append(cat_or_name)

                if filters_and:
                    cosmetics = query.filter(and_(*filters_and)).all()
                else:
                    # 필터를 만들 수 없다면 기존 product_name 전체로 검색
                    cosmetics = db.query(Cosmetic).filter(
                        Cosmetic.name.like(f"%{product_name}%")
                    ).all()
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass
                logger.error("제품명 검색 실패", exc_info=True)
                return "시스템 오류로 제품 정보를 조회하지 못했습니다. 잠시 후 다시 시도해주세요."
            
            # 3. 결과 처리: 0/1/여러 개
            if not cosmetics:
                # 3-1. 하이브리드 Fallback: 브랜드/카테고리 기반 의미 검색
                try:
                    fallback_query = " ".join([
                        " ".join(brand_tokens),
                        category_token or "",
                        "제품"
                    ]).strip()
                    vs_results = VectorStoreService.search_cosmetics(
                        db=db,
                        query=fallback_query,
                        filters={},
                        limit=5
                    )
                    if vs_results:
                        ids = [r['cosmetic_id'] for r in vs_results]
                        cosmetics = CosmeticRepository.get_by_ids(db, ids)
                except Exception:
                    try:
                        db.rollback()
                    except Exception:
                        pass
                    cosmetics = []
                
                if not cosmetics:
                    return f"'{product_name}' 제품을 찾을 수 없습니다.\n\n브랜드와 카테고리를 함께 알려주시면 더 정확히 찾아드릴 수 있어요. (예: '에스트라 크림')"
            
            # 4. 여러 결과가 있으면 목록 반환
            if len(cosmetics) > 1:
                result = f"'{product_name}'로 검색한 결과 {len(cosmetics)}개가 있습니다:\n\n"
                for i, cosmetic in enumerate(cosmetics[:5], 1):  # 최대 5개
                    result += f"{i}. {cosmetic.name} ({cosmetic.brand})\n"
                result += "\n더 정확한 제품명을 알려주시면 상세 정보를 제공하겠습니다."
                return result
            
            # 5. 단일 제품 상세 정보
            cosmetic = cosmetics[0]
            
            # 상세 정보 포맷팅 (기존 get_detail 재사용)
            detail = CosmeticRepository.get_detail(db, cosmetic.cosmetic_id, member_id)
            
            if not detail:
                return f"'{cosmetic.name}' 제품의 상세 정보를 조회할 수 없습니다."
            
            result = f"**{detail['name']}**\n\n"
            result += f"🏷️ **브랜드**: {detail['brand']}\n"
            result += f"💰 **가격**: {int(detail['price']):,}원\n"
            result += f"📦 **카테고리**: {detail['category']}\n\n"
            
            if detail.get('main_effect'):
                result += f"✨ **주요 효능**: {detail['main_effect']}\n"
            if detail.get('key_ingredient'):
                result += f"🧪 **핵심 성분**: {detail['key_ingredient']}\n"
            if detail.get('care_symptom'):
                result += f"💊 **케어 증상**: {detail['care_symptom']}\n"
            if detail.get('skin_type'):
                result += f"👤 **피부 타입**: {detail['skin_type']}\n"
            if detail.get('skin_disease'):
                result += f"🏥 **관련 질환**: {detail['skin_disease']}\n"
            
            result += "\n"
            
            if detail.get('short_description'):
                result += f"📝 **한줄 설명**: {detail['short_description']}\n\n"
            
            if detail.get('description'):
                result += f"📄 **상세 설명**:\n{detail['description']}\n\n"
            
            if detail.get('buy_url'):
                result += f"🔗 **구매하기**: {detail['buy_url']}\n\n"
            
            result += "💡 추가 정보가 필요하시면 질문해주세요!"
            
            return result
            
        except Exception as e:
            logger.error(f"제품 상세 정보 조회 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"제품 상세 정보 조회 중 오류가 발생했습니다: {str(e)}"
    
    return get_product_detail_impl


def get_chat_tools(db: Session, member_id: int) -> list:
    """
    Agent에 전달할 Tool 리스트 생성
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        list: Tool 함수 리스트
    """
    return [
        create_diagnosis_history_tool(db, member_id),
        create_recommended_products_tool(db, member_id),
        create_recommend_by_symptom_tool(db, member_id),
        create_request_rediagnosis_tool(),
        create_get_product_detail_tool(db, member_id)
    ]

