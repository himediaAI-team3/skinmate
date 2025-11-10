"""
LangChain Tool 정의 - 진단 이력 및 추천 제품 조회
"""
from contextvars import ContextVar
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from app.repository.analysis import AnalysisRepository
from app.repository.recommendation import RecommendationRepository
from app.repository.cosmetic import CosmeticRepository
from app.repository.diagnosis import DiagnosisRepository


# Thread-safe한 Context Variables 사용
_db_session: ContextVar[Session] = ContextVar('db_session', default=None)
_current_member_id: ContextVar[int] = ContextVar('current_member_id', default=None)
_thread_id: ContextVar[str] = ContextVar('thread_id', default=None)


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


# Tool 리스트 (Agent에서 사용)
TOOLS = [get_my_diagnosis_history, get_recommended_products]