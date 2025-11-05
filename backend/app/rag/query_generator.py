from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm


SYSTEM_PROMPT = (
    "당신은 10년 경력의 피부 관리 전문가이자 검색 전략가입니다.\n"
    "고객의 피부 진단 결과를 바탕으로, 화장품 지식 DB에서 적합한 상품을 찾기 위한 검색 쿼리를 생성하세요.\n\n"
    "## 출력 형식 (JSON만)\n"
    "{\n"
    "  \"text_query\": \"자연어 검색 쿼리 (150-250자, 피부타입 포함)\",\n"
    "  \"keywords\": [\"효능 키워드 5-10개\"],\n"
    "  \"price_filter\": {\"gte\": 최소가격, \"lte\": 최대가격} 또는 null\n"
    "}\n\n"
    "## 입력(예상)\n"
    "- disease_name: 질환명\n"
    "- summary: 핵심 증상/요약\n"
    "- skin_type: 피부타입\n"
    "- min_price, max_price: 가격 범위 (없으면 null)\n\n"
    "## 작성 원칙 (강화 버전)\n"
    "1) text_query\n"
    "   - 문장 첫 부분에 피부타입 명시\n"
    "   - 질환의 핵심 증상과 필요한 효능을 구체적으로 기술 (제품 형태/특성 포함 가능)\n"
    "   - 회피 요소는 간접 반영 문구 사용 (저자극/무향 등), 150~250자, 한국어, 의약 표현 금지\n"
    "2) keywords\n"
    "   - DB에 실제로 존재할 법한 명사형 효능/증상, 5~10개, 상충 단어 제외, 중복 금지\n"
    "3) price_filter\n"
    "   - min/max 둘 다 숫자면 {gte, lte}, 아니면 null\n"
    "4) 안전 수칙(간접 반영)\n"
    "   - 민감/주사: 저자극 무향 등, 여드름/지성: 논코메도제닉/피지조절, 아토피/건성: 고보습/장벽강화/진정\n"
    "5) 형식·품질\n"
    "   - 오직 JSON 객체만 반환, ASCII 따옴표, null은 소문자, 가격은 숫자만\n\n"
    "## 에러 처리\n"
    "- 입력 필수값 누락 또는 내부 오류 시 아래 기본 형식으로 반환\n"
    "{\n"
    "  \"text_query\": \"{skin_type} 피부의 {disease_name} 증상 완화를 위한 저자극 케어 제품으로, 핵심 증상에 맞춘 {핵심 효능} 중심의 데일리 사용 적합\",\n"
    "  \"keywords\": [\"보습\", \"진정\"],\n"
    "  \"price_filter\": {\"gte\": min_price, \"lte\": max_price} 또는 null\n"
    "}\n\n"
    "예시 1 / 예시 2는 생략하고 원칙만 따르세요."
)


def _fallback_query(diagnosis_info: Dict[str, Any]) -> Dict[str, Any]:
    disease_name = (diagnosis_info.get("disease_name") or "").strip() or "피부"
    skin_type = (diagnosis_info.get("skin_type") or "").strip() or "일반"
    min_price = diagnosis_info.get("min_price")
    max_price = diagnosis_info.get("max_price")

    price_filter: Optional[Dict[str, int]] = None
    if isinstance(min_price, (int, float)) and isinstance(max_price, (int, float)):
        price_filter = {"gte": int(min_price), "lte": int(max_price)}

    text_query = (
        f"{skin_type} 피부의 {disease_name} 증상 완화를 위한 저자극 데일리 케어 제품으로, "
        "핵심 증상에 맞춘 보습·진정 중심의 사용을 고려"
    )

    return {
        "text_query": text_query,
        "keywords": ["보습", "진정"],
        "price_filter": price_filter,
    }


def _build_chain() -> Runnable:
    llm = get_llm(temperature=0.3)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "입력:\n{input_json}\n\n오직 JSON 객체만 반환하세요.",
            ),
        ]
    )

    parser = JsonOutputParser()
    chain: Runnable = (prompt | llm | parser).with_config(run_name="query_generation")
    return chain


def generate_search_query(diagnosis_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate search query spec from diagnosis info using LLM.

    Args:
        diagnosis_info (Dict[str, Any]):
            {
              "disease_name": str,
              "summary": str,
              "skin_type": Optional[str],
              "min_price": Optional[int],
              "max_price": Optional[int]
            }

    Returns:
        Dict[str, Any]:
            {
              "text_query": str,
              "keywords": List[str],
              "price_filter": Optional[Dict[str, int]]
            }

    Notes:
        - Retries once on failure, then returns fallback.
    """

    chain = _build_chain()
    payload = {"input_json": json.dumps(diagnosis_info, ensure_ascii=True)}

    try:
        result = chain.invoke(payload)
        if not isinstance(result, dict):  # parser guarantees dict, but guard anyway
            raise ValueError("LLM 출력 형식 오류")
        # Normalize price_filter if present
        pf = result.get("price_filter")
        if pf is not None and isinstance(pf, dict):
            try:
                gte = pf.get("gte")
                lte = pf.get("lte")
                if isinstance(gte, (int, float)) and isinstance(lte, (int, float)):
                    result["price_filter"] = {"gte": int(gte), "lte": int(lte)}
                else:
                    result["price_filter"] = None
            except Exception:
                result["price_filter"] = None
        return result
    except Exception:
        # retry once
        try:
            result = chain.invoke(payload)
            if not isinstance(result, dict):
                raise ValueError("LLM 출력 형식 오류")
            return result
        except Exception:
            return _fallback_query(diagnosis_info)


__all__ = ["generate_search_query"]


