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
        """
        사용자 메시지에서 refine query 키워드 추출 (LLM + Fallback)
        
        LLM을 사용하여 의미 기반 키워드 추출을 시도하고, 실패 시 패턴 매칭으로 fallback합니다.
        예: "촉촉한 제품 추천해줘" → ["수분감", "보습"]
        
        Args:
            message: 사용자 메시지
            
        Returns:
            List[str]: 추출된 키워드 리스트 (최대 5개)
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
        """
        진단/분석 상태와 제외할 제품 ID 로드
        
        Args:
            db: DB 세션
            latest_analysis_id: 최근 진단 ID
            
        Returns:
            Tuple[Any, Any, List[int]] | str: 성공 시 (diagnosis, analysis, excluded_ids),
                                             실패 시 에러 메시지 문자열
        """
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
        """
        원본 쿼리와 refine 키워드로 dense/sparse 재검색 쿼리 구성
        
        refine 키워드가 있으면 원본 쿼리에 키워드를 추가하여 확장합니다.
        
        Args:
            original_query: 원본 검색 쿼리 (dense_query, sparse_keywords)
            refine_keywords: refine 키워드 리스트 (예: ["수분감", "진정"])
            
        Returns:
            Tuple[str, str]: (refined_dense_query, refined_sparse_query)
        """
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
        """
        캐시에서 해당 thread/analysis 후보 목록 조회
        
        캐시가 없거나 다른 진단의 캐시이면 빈 리스트를 반환합니다.
        
        Args:
            get_cache: 캐시 조회 함수
            thread_id: 대화 세션 ID
            latest_analysis_id: 최근 진단 ID
            
        Returns:
            List[int]: 추천 후보 화장품 ID 리스트 (없거나 만료 시 빈 리스트)
        """
        cache = get_cache(thread_id)
        if cache and cache.get("analysis_id") != latest_analysis_id:
            logger.info(f"[ALT] cache exists but analysis_id mismatch (cache={cache.get('analysis_id')}, current={latest_analysis_id})")
            return []
        candidates = cache.get("candidate_cosmetic_ids", []) if cache else []
        logger.info(f"[ALT] thread_id={thread_id}, analysis_id={latest_analysis_id}, cache_exists={bool(cache)}, cache_candidates={len(candidates)}")
        return candidates

    @staticmethod
    def fetch_cosmetics_by_ids(db: Session, ids: List[int]) -> List[dict]:
        """
        cosmetic_id 목록으로 상세 정보를 조회하여 dict 리스트로 반환
        
        Args:
            db: DB 세션
            ids: 화장품 ID 리스트
            
        Returns:
            List[dict]: 화장품 상세 정보 리스트
        """
        cosmetics: List[dict] = []
        for cid in ids:
            detail = CosmeticRepository.get_detail(db, cid)
            if detail:
                cosmetics.append(detail)
        return cosmetics

    @staticmethod
    def format_products(cosmetics: List[dict], header: str) -> str:
        """
        제품 리스트를 공통 포맷으로 문자열 생성
        
        Args:
            cosmetics: 화장품 상세 정보 리스트
            header: 헤더 문자열
            
        Returns:
            str: 포맷팅된 제품 목록 문자열
        """
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
        """
        캐시에 후보가 충분하면 3개 반환하고 캐시 갱신, 아니면 None
        
        캐시에서 3개 이상의 후보가 있으면 상위 3개를 조회하여 반환하고,
        사용한 3개를 캐시에서 제거합니다.
        
        Args:
            db: DB 세션
            thread_id: 대화 세션 ID
            candidates: 추천 후보 화장품 ID 리스트
            update_cache: 캐시 갱신 함수
            
        Returns:
            str | None: 포맷팅된 제품 목록 문자열 (후보 부족 시 None)
        """
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
        """
        검색 결과 기반으로 캐시를 초기화/갱신
        
        RAG 검색 결과 10개 중 상위 3개는 사용자에게 반환하고,
        나머지 7개는 캐시에 저장하여 다음 요청 시 사용합니다.
        
        Args:
            init_cache: 캐시 초기화 함수
            thread_id: 대화 세션 ID
            analysis_id: 진단 ID
            search_results: RAG 검색 결과 리스트 (10개)
            used_top3_ids: 사용한 상위 3개 화장품 ID 리스트
        """
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
        """
        RAG 재검색 실행, 캐시 갱신, 결과 포맷 후 반환
        
        사용자 메시지에서 refine 키워드를 추출하여 검색 쿼리를 확장하고,
        Qdrant에서 하이브리드 검색을 수행합니다. 검색 결과 10개 중 상위 3개를
        반환하고 나머지 7개는 캐시에 저장합니다.
        
        Args:
            db: DB 세션
            latest_analysis_id: 최근 진단 ID
            excluded_ids: 제외할 화장품 ID 리스트 (이미 추천받은 제품)
            user_message: 사용자 메시지 (refine 키워드 추출용)
            thread_id: 대화 세션 ID
            init_cache: 캐시 초기화 함수
            
        Returns:
            str: 포맷팅된 제품 목록 문자열
        """
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


