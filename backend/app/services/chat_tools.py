"""
LangChain Tool 정의 - 진단 이력 및 추천 제품 조회
"""
from contextvars import ContextVar
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from typing import List
import logging
from app.repository.analysis import AnalysisRepository
from app.repository.recommendation import RecommendationRepository
from app.repository.cosmetic import CosmeticRepository
from app.repository.diagnosis import DiagnosisRepository
from app.services.vector_store import VectorStoreService
from app.services.alternative_recommendation import AlternativeRecommendationService


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

    state = AlternativeRecommendationService.load_state(db, latest_analysis_id)
    if isinstance(state, str):
        return state
    _diagnosis, _analysis, excluded_ids = state

    candidates = AlternativeRecommendationService.get_cache_candidates(
        get_cache=get_recommendation_cache,
        thread_id=thread_id,
        latest_analysis_id=latest_analysis_id
    )
    cached = AlternativeRecommendationService.return_from_cache_if_possible(
        db=db,
        thread_id=thread_id,
        candidates=candidates,
        update_cache=update_recommendation_cache,
    )
    if cached is not None:
        return cached

    return AlternativeRecommendationService.run_rag_and_prepare_response(
        db=db,
        latest_analysis_id=latest_analysis_id,
        excluded_ids=excluded_ids,
        user_message=user_message,
        thread_id=thread_id,
        init_cache=init_recommendation_cache,
    )

# Tool 리스트 (Agent에서 사용)
TOOLS = [get_my_diagnosis_history, get_recommended_products, get_alternative_recommendations]