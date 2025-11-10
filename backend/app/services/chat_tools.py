"""
LangChain Tool 정의 - 진단 이력 및 추천 제품 조회
"""
from contextvars import ContextVar
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session
from typing import List
import logging
from app.repository.analysis import AnalysisRepository
from app.repository.recommendation import RecommendationRepository
from app.repository.cosmetic import CosmeticRepository
from app.repository.diagnosis import DiagnosisRepository
from app.core.config.llm import get_llm
from app.services.vector_store import VectorStoreService


# Thread-safe한 Context Variables 사용
_db_session: ContextVar[Session] = ContextVar('db_session', default=None)
_current_member_id: ContextVar[int] = ContextVar('current_member_id', default=None)
_thread_id: ContextVar[str] = ContextVar('thread_id', default=None)
_recommendation_cache: ContextVar[dict] = ContextVar('recommendation_cache', default={})

logger = logging.getLogger(__name__)


def set_tool_context(db: Session, member_id: int):
    """Tool에서 사용할 DB 세션과 member_id 설정 (Thread-safe)"""
    _db_session.set(db)
    _current_member_id.set(member_id)

def set_thread_id(thread_id: str) -> None:
    """현재 대화 thread_id 설정"""
    _thread_id.set(thread_id)

def get_thread_id() -> str:
    """현재 대화 thread_id 조회"""
    return _thread_id.get()

def init_recommendation_cache(thread_id: str, analysis_id: int, candidates: List[int]) -> None:
    """thread_id 기반 추천 후보 캐시 초기화"""
    cache = _recommendation_cache.get()
    if not isinstance(cache, dict):
        cache = {}
    cache[thread_id] = {
        "analysis_id": analysis_id,
        "candidate_cosmetic_ids": list(candidates) if candidates else [],
    }
    _recommendation_cache.set(cache)

def get_recommendation_cache(thread_id: str) -> dict | None:
    """thread_id 기반 추천 후보 캐시 조회"""
    cache = _recommendation_cache.get()
    if not isinstance(cache, dict):
        return None
    return cache.get(thread_id)

def update_recommendation_cache(thread_id: str, used_cosmetic_ids: List[int]) -> None:
    """방금 사용한 후보 제거하여 캐시 갱신"""
    cache = _recommendation_cache.get()
    if not isinstance(cache, dict):
        return
    if thread_id in cache:
        remaining = [
            cid for cid in cache[thread_id].get("candidate_cosmetic_ids", [])
            if cid not in set(used_cosmetic_ids or [])
        ]
        cache[thread_id]["candidate_cosmetic_ids"] = remaining
        _recommendation_cache.set(cache)


def extract_refine_keywords(message: str) -> List[str]:
    """
    사용자 메시지에서 refine query 키워드 추출 (LLM + Fallback)
    """
    try:
        llm = get_llm(temperature=0.3)
        prompt = f"""사용자가 화장품 추천에서 원하는 속성이나 개선 포인트를 요약해서 키워드만 뽑아주세요.
예: 수분감, 진정, 트러블, 민감성, 모공, 끈적임 없음, 유분 적음 등

---
"{message}"

키워드를 쉼표로 구분하여 나열하세요 (최대 5개):"""
        response = llm.invoke([HumanMessage(content=prompt)])
        keywords_text = response.content.strip()
        keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
        keywords = list(dict.fromkeys(keywords))
        logger.info(f"LLM 키워드 추출 성공: {keywords}")
        return keywords[:5]
    except Exception as e:
        logger.warning(f"LLM 키워드 추출 실패, fallback 사용: {e}")
        fallback_keywords = []
        keyword_patterns = [
            "수분", "보습", "진정", "트러블", "민감", "자극",
            "홍조", "각질", "탄력", "미백", "주름", "모공",
            "유분", "끈적", "번들", "피지", "가려움", "건조"
        ]
        for kw in keyword_patterns:
            if kw in message:
                fallback_keywords.append(kw)
        logger.info(f"Fallback 키워드 추출: {fallback_keywords}")
        return fallback_keywords

def _get_context():
    """DB, member_id, thread_id, latest_analysis_id 검증/획득. 실패 시 에러 문구 반환."""
    db = _db_session.get()
    member_id = _current_member_id.get()
    thread_id = get_thread_id()
    if not db or not member_id:
        return "오류: 사용자 정보를 확인할 수 없습니다."
    if not thread_id:
        return "오류: 대화 세션 정보를 확인할 수 없습니다."
    latest_analysis_id = _get_latest_analysis_id()
    if not latest_analysis_id:
        return "진단 이력이 없어서 추천 제품을 확인할 수 없습니다. 먼저 피부 진단을 받아보세요!"
    return {"db": db, "member_id": member_id, "thread_id": thread_id, "latest_analysis_id": latest_analysis_id}

def _load_state(db: Session, latest_analysis_id: int):
    """진단/분석 상태와 제외 ID 로드. 실패 시 에러 문구 반환."""
    diagnosis = DiagnosisRepository.get_by_analysis_id(db, latest_analysis_id)
    analysis = AnalysisRepository.get_by_id(db, latest_analysis_id)
    if not diagnosis or not analysis:
        return "진단 정보를 찾을 수 없습니다."
    existing = RecommendationRepository.get_by_analysis_id(db, latest_analysis_id)
    excluded_ids = [rec.cosmetic_id for rec in existing]
    logger.info(f"제외할 제품 ID: {excluded_ids}")
    return diagnosis, analysis, excluded_ids

def _fetch_cosmetics_by_ids(db: Session, ids: List[int]) -> List[dict]:
    """cosmetic_id 목록으로 상세 정보를 조회하여 dict 리스트로 반환"""
    cosmetics: List[dict] = []
    for cid in ids:
        detail = CosmeticRepository.get_detail(db, cid)
        if detail:
            cosmetics.append(detail)
    return cosmetics

def _format_products(cosmetics: List[dict], header: str) -> str:
    """제품 리스트를 공통 포맷으로 문자열 생성"""
    lines: List[str] = [header, ""]
    for idx, cosmetic in enumerate(cosmetics, 1):
        lines.append(f"{idx}. {cosmetic['name']}")
        lines.append(f"   브랜드: {cosmetic['brand']}")
        lines.append(f"   가격: {int(cosmetic['price']):,}원")
        if cosmetic.get("main_effect"):
            lines.append(f"   주요 효능: {cosmetic['main_effect']}")
        lines.append("")
    return "\n".join(lines)

def _build_refined_queries(original_query: dict, refine_keywords: List[str]) -> tuple[str, str]:
    """원본 쿼리와 키워드로 dense/sparse 재검색 쿼리 구성"""
    if not refine_keywords:
        return original_query["dense_query"], original_query["sparse_keywords"]
    refined_sparse = original_query["sparse_keywords"] + " " + " ".join(refine_keywords)
    refined_dense = (
        original_query["dense_query"]
        + f" 특히 {', '.join(refine_keywords)}에 집중한 제품이 필요합니다."
    )
    return refined_dense, refined_sparse

def _update_cache_after_search(
    thread_id: str,
    analysis_id: int,
    search_results: List[dict],
    used_top3_ids: List[int],
) -> None:
    """검색 결과 기반으로 캐시를 초기화/갱신한다."""
    remaining_candidates = [r["cosmetic_id"] for r in search_results[3:]]
    init_recommendation_cache(thread_id, analysis_id, remaining_candidates)
    logger.info(f"[ALT] returned_top3={used_top3_ids}, cached_remaining={len(remaining_candidates)}")

def _get_cache_candidates(thread_id: str, latest_analysis_id: int) -> List[int]:
    """캐시에서 해당 thread/analysis 후보 목록 조회(없거나 만료 시 빈 리스트)."""
    cache = get_recommendation_cache(thread_id)
    if cache and cache.get("analysis_id") != latest_analysis_id:
        logger.info(f"[ALT] cache exists but analysis_id mismatch (cache={cache.get('analysis_id')}, current={latest_analysis_id})")
        return []
    candidates = cache.get("candidate_cosmetic_ids", []) if cache else []
    logger.info(f"[ALT] thread_id={thread_id}, analysis_id={latest_analysis_id}, cache_exists={bool(cache)}, cache_candidates={len(candidates)}")
    return candidates

def _return_from_cache_if_possible(db: Session, thread_id: str, candidates: List[int]) -> str | None:
    """캐시에 후보가 충분하면 3개 반환하고 캐시 갱신, 아니면 None."""
    if len(candidates) >= 3:
        next_3 = candidates[:3]
        logger.info(f"[ALT] using_cache: next_3={next_3}, remaining={len(candidates) - 3}")
        cosmetics = _fetch_cosmetics_by_ids(db, next_3)
        update_recommendation_cache(thread_id, next_3)
        header = "다른 추천 화장품 (TOP 3):\n\n"
        return _format_products(cosmetics, header)
    return None

def _run_rag_and_prepare_response(
    db: Session,
    latest_analysis_id: int,
    excluded_ids: List[int],
    user_message: str,
    thread_id: str,
) -> str:
    """RAG 재검색 실행, 캐시 갱신, 결과 포맷 후 반환."""
    refine_keywords = extract_refine_keywords(user_message)
    logger.info(f"Refine keywords 감지: {refine_keywords}, RAG 재검색 시작")
    diagnosis = DiagnosisRepository.get_by_analysis_id(db, latest_analysis_id)
    analysis = AnalysisRepository.get_by_id(db, latest_analysis_id)
    if not diagnosis or not analysis:
        return "진단 정보를 찾을 수 없습니다."
    from app.services.recommendation import RecommendationService
    original_query = RecommendationService._build_search_query_from_diagnosis(db, latest_analysis_id)
    query_dense, query_sparse = _build_refined_queries(original_query, refine_keywords)
    if refine_keywords:
        logger.info(f"Refined Dense Query: {query_dense}")
        logger.info(f"Refined Sparse Query: {query_sparse}")
    else:
        logger.info("refine 키워드 없음 → 기본 쿼리로 대체 추천 검색")
    logger.info(f"[ALT] must_not(excluded)={excluded_ids} (n={len(excluded_ids)})")
    search_results = VectorStoreService.search_hybrid(
        query_dense_text=query_dense,
        query_sparse_text=query_sparse,
        min_price=analysis.min_price or 0,
        max_price=analysis.max_price or 999999,
        skin_type=analysis.skin_type,
        disease_name=diagnosis.disease_name,
        excluded_cosmetic_ids=excluded_ids,
        limit=10
    )
    logger.info(f"[ALT] search_results_count={len(search_results)}")
    logger.info(f"RAG 재검색 결과: {len(search_results)}개")
    if len(search_results) == 0:
        return "조건에 맞는 새로운 화장품을 찾을 수 없습니다. 새로운 진단을 받아보세요."
    top3_ids = [r['cosmetic_id'] for r in search_results[:3]]
    cosmetics = _fetch_cosmetics_by_ids(db, top3_ids)
    _update_cache_after_search(thread_id, latest_analysis_id, search_results, top3_ids)
    header = f"'{', '.join(refine_keywords)}' 조건으로 다시 검색한 결과입니다:\n\n" if refine_keywords else "기존 추천을 제외한 다른 화장품 추천 (TOP 3):\n\n"
    return _format_products(cosmetics, header)


def _get_latest_analysis_id():
    """최근 진단의 analysis_id 조회"""
    db = _db_session.get()
    member_id = _current_member_id.get()
    results = AnalysisRepository.get_by_member_id_with_pagination(
        db, 
        member_id, 
        page=1, 
        size=1
    )
    return results[0][0] if results else None


@tool
def get_my_diagnosis_history() -> str:
    """
    사용자의 최근 피부 진단 이력을 조회합니다.
    
    Returns:
        str: 최근 진단 결과 (진단일, 진단명, 증상 요약)
    """
    db = _db_session.get()
    member_id = _current_member_id.get()
    
    if not db or not member_id:
        return "오류: 사용자 정보를 확인할 수 없습니다."
    
    # 최근 5개 진단 이력 조회
    results = AnalysisRepository.get_by_member_id_with_pagination(
        db, 
        member_id, 
        page=1, 
        size=5
    )
    
    if not results:
        return "진단 이력이 없습니다. 먼저 피부 진단을 받아보세요!"
    
    # 결과 포맷팅
    history_text = "최근 진단 이력:\n\n"
    for idx, (analysis_id, disease_name, created_at) in enumerate(results, 1):
        # 진단 상세 정보 조회
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
        summary = diagnosis.summary if diagnosis else "요약 없음"
        
        history_text += f"{idx}. 진단일: {created_at.strftime('%Y년 %m월 %d일')}\n"
        history_text += f"   진단명: {disease_name}\n"
        history_text += f"   요약: {summary}\n\n"
    
    return history_text


@tool
def get_recommended_products() -> str:
    """
    사용자의 최근 진단 결과를 기반으로 AI가 추천한 화장품 3개를 조회합니다.
    
    Returns:
        str: 추천 화장품 목록 (제품명, 브랜드, 가격, 추천 이유)
    """
    db = _db_session.get()
    member_id = _current_member_id.get()
    
    if not db or not member_id:
        return "오류: 사용자 정보를 확인할 수 없습니다."
    
    # 최근 진단 이력 조회
    latest_analysis_id = _get_latest_analysis_id()
    
    if not latest_analysis_id:
        return "진단 이력이 없어서 추천 제품을 확인할 수 없습니다. 먼저 피부 진단을 받아보세요!"
    
    # 추천 제품 조회
    recommendations = RecommendationRepository.get_by_analysis_id(db, latest_analysis_id)
    
    if not recommendations:
        return "아직 추천 제품이 없습니다. 진단 결과를 기다려주세요."
    
    # TOP3 추천 ID 로깅
    top3_ids = [rec.cosmetic_id for rec in recommendations[:3]]
    logger.info(f"[RECO] initial TOP3 ids={top3_ids}")
    
    # 제품 상세 정보 조회 및 포맷팅
    product_text = "AI 추천 화장품 (TOP 3):\n\n"
    for rec in recommendations[:3]:  # TOP 3만
        cosmetic = CosmeticRepository.get_detail(db, rec.cosmetic_id)
        if cosmetic:
            product_text += f"{rec.ranking}. {cosmetic['name']}\n"
            product_text += f"   브랜드: {cosmetic['brand']}\n"
            product_text += f"   가격: {int(cosmetic['price']):,}원\n"
            product_text += f"   추천 이유: {rec.reason}\n"
            if cosmetic['main_effect']:
                product_text += f"   주요 효능: {cosmetic['main_effect']}\n"
            product_text += "\n"
    
    return product_text


@tool
def get_alternative_recommendations(user_message: str = "") -> str:
    """
    사용자의 최근 진단을 바탕으로 이전에 추천받은 화장품을 제외한 다른 화장품 3개를 추천합니다.
    """
    ctx = _get_context()
    if isinstance(ctx, str):
        return ctx
    db = ctx["db"]
    thread_id = ctx["thread_id"]
    latest_analysis_id = ctx["latest_analysis_id"]

    state = _load_state(db, latest_analysis_id)
    if isinstance(state, str):
        return state
    _diagnosis, _analysis, excluded_ids = state

    candidates = _get_cache_candidates(thread_id, latest_analysis_id)
    cached = _return_from_cache_if_possible(db, thread_id, candidates)
    if cached is not None:
        return cached

    return _run_rag_and_prepare_response(
        db=db,
        latest_analysis_id=latest_analysis_id,
        excluded_ids=excluded_ids,
        user_message=user_message,
        thread_id=thread_id,
    )

# Tool 리스트 (Agent에서 사용)
TOOLS = [get_my_diagnosis_history, get_recommended_products, get_alternative_recommendations]