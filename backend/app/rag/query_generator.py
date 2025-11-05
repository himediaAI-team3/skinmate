from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm
from app.rag.prompts import QUERY_SYSTEM_PROMPT


SYSTEM_PROMPT = QUERY_SYSTEM_PROMPT


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


