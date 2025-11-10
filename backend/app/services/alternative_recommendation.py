"""
대체 추천 로직 전용 서비스 모듈
- RAG 재검색, 캐시 계산, 결과 포맷팅 등 비즈니스 로직을 담당
"""
from typing import List, Tuple, Callable, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.repository.recommendation import RecommendationRepository
from app.repository.cosmetic import CosmeticRepository
from app.repository.diagnosis import DiagnosisRepository
from app.repository.analysis import AnalysisRepository
from app.core.config.llm import get_llm
from app.services.vector_store import VectorStoreService
from langchain_core.messages import HumanMessage


logger = logging.getLogger(__name__)


class AlternativeRecommendationService:
    @staticmethod
    def extract_refine_keywords(message: str) -> List[str]:
        """사용자 메시지에서 refine query 키워드 추출 (LLM + Fallback)"""
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
            # 중복 제거, 최대 5개
            return list(dict.fromkeys(keywords))[:5]
        except Exception as e:
            logger.warning(f"LLM 키워드 추출 실패, fallback 사용: {e}")
            fallback_keywords: List[str] = []
            keyword_patterns = [
                "수분", "보습", "진정", "트러블", "민감", "자극",
                "홍조", "각질", "탄력", "미백", "주름", "모공",
                "유분", "끈적", "번들", "피지", "가려움", "건조"
            ]
            for kw in keyword_patterns:
                if kw in message:
                    fallback_keywords.append(kw)
            return fallback_keywords

    @staticmethod
    def load_state(db: Session, latest_analysis_id: int) -> Tuple[Any, Any, List[int]] | str:
        """진단/분석 상태와 제외 ID 로드. 실패 시 에러 문구 반환."""
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, latest_analysis_id)
        analysis = AnalysisRepository.get_by_id(db, latest_analysis_id)
        if not diagnosis or not analysis:
            return "진단 정보를 찾을 수 없습니다."
        existing = RecommendationRepository.get_by_analysis_id(db, latest_analysis_id)
        excluded_ids = [rec.cosmetic_id for rec in existing]
        logger.info(f"제외할 제품 ID: {excluded_ids}")
        return diagnosis, analysis, excluded_ids

    @staticmethod
    def build_refined_queries(original_query: dict, refine_keywords: List[str]) -> Tuple[str, str]:
        """원본 쿼리와 키워드로 dense/sparse 재검색 쿼리 구성"""
        if not refine_keywords:
            return original_query["dense_query"], original_query["sparse_keywords"]
        refined_sparse = original_query["sparse_keywords"] + " " + " ".join(refine_keywords)
        refined_dense = (
            original_query["dense_query"]
            + f" 특히 {', '.join(refine_keywords)}에 집중한 제품이 필요합니다."
        )
        return refined_dense, refined_sparse

    @staticmethod
    def get_cache_candidates(
        get_cache: Callable[[str], dict | None],
        thread_id: str,
        latest_analysis_id: int
    ) -> List[int]:
        """캐시에서 해당 thread/analysis 후보 목록 조회(없거나 만료 시 빈 리스트)."""
        cache = get_cache(thread_id)
        if cache and cache.get("analysis_id") != latest_analysis_id:
            logger.info(f"[ALT] cache exists but analysis_id mismatch (cache={cache.get('analysis_id')}, current={latest_analysis_id})")
            return []
        candidates = cache.get("candidate_cosmetic_ids", []) if cache else []
        logger.info(f"[ALT] thread_id={thread_id}, analysis_id={latest_analysis_id}, cache_exists={bool(cache)}, cache_candidates={len(candidates)}")
        return candidates

    @staticmethod
    def fetch_cosmetics_by_ids(db: Session, ids: List[int]) -> List[dict]:
        cosmetics: List[dict] = []
        for cid in ids:
            detail = CosmeticRepository.get_detail(db, cid)
            if detail:
                cosmetics.append(detail)
        return cosmetics

    @staticmethod
    def format_products(cosmetics: List[dict], header: str) -> str:
        lines: List[str] = [header, ""]
        for idx, cosmetic in enumerate(cosmetics, 1):
            lines.append(f"{idx}. {cosmetic['name']}")
            lines.append(f"   브랜드: {cosmetic['brand']}")
            lines.append(f"   가격: {int(cosmetic['price']):,}원")
            if cosmetic.get("main_effect"):
                lines.append(f"   주요 효능: {cosmetic['main_effect']}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def return_from_cache_if_possible(
        db: Session,
        thread_id: str,
        candidates: List[int],
        update_cache: Callable[[str, List[int]], None],
    ) -> str | None:
        """캐시에 후보가 충분하면 3개 반환하고 캐시 갱신, 아니면 None."""
        if len(candidates) >= 3:
            next_3 = candidates[:3]
            logger.info(f"[ALT] using_cache: next_3={next_3}, remaining={len(candidates) - 3}")
            cosmetics = AlternativeRecommendationService.fetch_cosmetics_by_ids(db, next_3)
            update_cache(thread_id, next_3)
            header = "다른 추천 화장품 (TOP 3):\n\n"
            return AlternativeRecommendationService.format_products(cosmetics, header)
        return None

    @staticmethod
    def update_cache_after_search(
        init_cache: Callable[[str, int, List[int]], None],
        thread_id: str,
        analysis_id: int,
        search_results: List[Dict[str, Any]],
        used_top3_ids: List[int],
    ) -> None:
        remaining_candidates = [r["cosmetic_id"] for r in search_results[3:]]
        init_cache(thread_id, analysis_id, remaining_candidates)
        logger.info(f"[ALT] returned_top3={used_top3_ids}, cached_remaining={len(remaining_candidates)}")

    @staticmethod
    def run_rag_and_prepare_response(
        db: Session,
        latest_analysis_id: int,
        excluded_ids: List[int],
        user_message: str,
        thread_id: str,
        init_cache: Callable[[str, int, List[int]], None],
    ) -> str:
        """RAG 재검색 실행, 캐시 갱신, 결과 포맷 후 반환."""
        refine_keywords = AlternativeRecommendationService.extract_refine_keywords(user_message)
        logger.info(f"Refine keywords 감지: {refine_keywords}, RAG 재검색 시작")
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, latest_analysis_id)
        analysis = AnalysisRepository.get_by_id(db, latest_analysis_id)
        if not diagnosis or not analysis:
            return "진단 정보를 찾을 수 없습니다."
        from app.services.recommendation import RecommendationService
        original_query = RecommendationService._build_search_query_from_diagnosis(db, latest_analysis_id)
        query_dense, query_sparse = AlternativeRecommendationService.build_refined_queries(original_query, refine_keywords)
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
        cosmetics = AlternativeRecommendationService.fetch_cosmetics_by_ids(db, top3_ids)
        AlternativeRecommendationService.update_cache_after_search(
            init_cache=init_cache,
            thread_id=thread_id,
            analysis_id=latest_analysis_id,
            search_results=search_results,
            used_top3_ids=top3_ids
        )
        header = (
            f"'{', '.join(refine_keywords)}' 조건으로 다시 검색한 결과입니다:\n\n"
            if refine_keywords else
            "기존 추천을 제외한 다른 화장품 추천 (TOP 3):\n\n"
        )
        return AlternativeRecommendationService.format_products(cosmetics, header)


