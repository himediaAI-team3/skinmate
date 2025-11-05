from __future__ import annotations

import json
from typing import Any, Dict, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm
from app.rag.prompts import QUERY_SYSTEM_PROMPT
from app.schemas.rag import DiagnosisInfo, QuerySpec, PriceFilter


SYSTEM_PROMPT = QUERY_SYSTEM_PROMPT


def _fallback_query(diagnosis_info: DiagnosisInfo) -> QuerySpec:
    disease_name = (diagnosis_info.disease_name or "").strip() or "피부"
    skin_type = (diagnosis_info.skin_type or "").strip() or "일반"

    pf: Optional[PriceFilter] = None
    if diagnosis_info.min_price is not None and diagnosis_info.max_price is not None:
        pf = PriceFilter(gte=int(diagnosis_info.min_price), lte=int(diagnosis_info.max_price))

    text_query = (
        f"{skin_type} 피부의 {disease_name} 증상 완화를 위한 저자극 데일리 케어 제품으로, "
        "핵심 증상에 맞춘 보습·진정 중심의 사용을 고려"
    )

    return QuerySpec(text_query=text_query, keywords=["보습", "진정"], price_filter=pf)


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


def generate_search_query(diagnosis_info: DiagnosisInfo | Dict[str, Any]) -> QuerySpec:
    """진단 정보를 기반으로 검색 질의 스펙을 생성합니다.

    Args:
        diagnosis_info (DiagnosisInfo | dict): 질환/피부타입/가격대 등 컨텍스트

    Returns:
        QuerySpec: 텍스트 쿼리, 키워드, 가격 필터를 포함한 스펙

    동작:
        - LLM 한 번 호출, 실패 시 한 번 재시도 후 폴백 반환
    """

    # 입력을 pydantic 모델로 정규화
    diag_model = diagnosis_info if isinstance(diagnosis_info, DiagnosisInfo) else DiagnosisInfo.model_validate(diagnosis_info)

    chain = _build_chain()
    payload = {"input_json": json.dumps(diag_model.model_dump(), ensure_ascii=True)}

    try:
        result = chain.invoke(payload)
        if not isinstance(result, dict):
            raise ValueError("LLM 출력 형식 오류")
        # Validate with pydantic
        # Coerce price_filter if present
        pf = result.get("price_filter")
        if isinstance(pf, dict) and pf:
            gte = pf.get("gte")
            lte = pf.get("lte")
            if gte is None or lte is None:
                result["price_filter"] = None
        return QuerySpec.model_validate(result)
    except Exception:
        # retry once
        try:
            result = chain.invoke(payload)
            if not isinstance(result, dict):
                raise ValueError("LLM 출력 형식 오류")
            return QuerySpec.model_validate(result)
        except Exception:
            return _fallback_query(diag_model)


__all__ = ["generate_search_query"]


