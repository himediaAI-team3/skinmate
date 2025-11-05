from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm


SYSTEM_PROMPT = """
당신은 10년 경력의 피부 관리 전문가입니다.
고객의 피부 진단 결과를 바탕으로 최적의 화장품 검색 쿼리를 생성하세요.

## 출력 형식 (JSON만)
{{
  "text_query": "자연어 검색 쿼리 (150-250자, 피부타입 포함)",
  "keywords": ["효능 키워드 5-10개"],
  "price_filter": {{"gte": 최소가격, "lte": 최대가격}} 또는 null
}}

## 작성 원칙
1. text_query: 피부타입을 문장 앞부분에 포함 ("건성 피부를 위한...")
2. text_query: 질환의 핵심 증상과 필요 효능을 구체적으로 서술
3. keywords: 데이터베이스에 실제 존재할 법한 명사형 단어 (보습, 진정, 피부장벽강화 등)
4. price_filter: 입력에 가격 정보 있으면 그대로 반영, 없으면 null

## Few-shot 예시
입력:
{{
  "disease_name": "아토피",
  "summary": "양쪽 볼 건조, 가려움, 홍조",
  "skin_type": "건성",
  "min_price": 20000,
  "max_price": 50000
}}

출력:
{{
  "text_query": "건성 피부의 아토피 증상을 완화하기 위한 고보습 진정 크림으로, 약해진 피부 장벽을 회복하고 건조함과 가려움을 집중 케어하는 저자극 제품",
  "keywords": ["보습", "진정", "피부장벽강화", "가려움완화", "건조", "홍조", "저자극"],
  "price_filter": {{"gte": 20000, "lte": 50000}}
}}

입력:
{{
  "disease_name": "여드름",
  "summary": "T존 피지 과다, 모공 막힘",
  "skin_type": "지성",
  "min_price": null,
  "max_price": null
}}

출력:
{{
  "text_query": "지성 피부의 과다 피지를 효과적으로 조절하고 막힌 모공을 정화하여 여드름을 케어하는 논코메도제닉 세럼",
  "keywords": ["피지조절", "모공케어", "진정", "트러블케어", "각질용해"],
  "price_filter": null
}}
"""


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


