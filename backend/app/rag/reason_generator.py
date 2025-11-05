from __future__ import annotations

from typing import Any, Dict

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm
from app.rag.prompts import REASON_SYSTEM_PROMPT


SYSTEM_PROMPT = REASON_SYSTEM_PROMPT


def _truncate_200(text: str) -> str:
    if len(text) <= 200:
        return text
    return text[:197] + "..."


def _fallback_reason(product: Document, diagnosis_info: Dict[str, Any]) -> str:
    brand = (product.metadata or {}).get("brand") or "이"
    disease = (diagnosis_info.get("disease_name") or "피부")
    return _truncate_200(f"{brand} 제품은 {disease} 케어에 효과적입니다.")


def _build_chain() -> Runnable:
    llm = get_llm(temperature=0.5)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                (
                    "제품 정보:\n{page_content}\n\n"
                    "브랜드: {brand}\n제품명: {product_name}\n카테고리: {category}\n가격: {price}원\n"
                    "제품 권장 피부타입(메타): {product_skin_type}\n"
                    "고객 정보:\n질환: {disease_name}\n피부타입(고객): {skin_type}\n순위: {rank}위\n\n"
                    "추천 이유를 200자 이내로 작성하세요."
                ),
            ),
        ]
    )
    chain: Runnable = (prompt | llm | StrOutputParser()).with_config(run_name="reason_generation")
    return chain


def generate_recommendation_reason(product: Document, diagnosis_info: Dict[str, Any], rank: int) -> str:
    """Generate a short recommendation reason for a product.

    Args:
        product (Document): Selected product document with metadata and page_content.
        diagnosis_info (Dict[str, Any]): Disease/user context.
        rank (int): Rank (1..3).

    Returns:
        str: Reason text (<=200 chars), with fallback on failure.
    """

    chain = _build_chain()
    md = product.metadata or {}
    try:
        text = chain.invoke(
            {
                "page_content": product.page_content or "",
                "brand": md.get("brand") or "",
                "product_name": md.get("name") or "",
                "category": md.get("category") or "",
                "price": md.get("price") or 0,
                "product_skin_type": md.get("skin_type") or "",
                "disease_name": diagnosis_info.get("disease_name") or "",
                "skin_type": diagnosis_info.get("skin_type") or "",
                "rank": rank,
            }
        )
        return _truncate_200(text or "")
    except Exception:
        return _fallback_reason(product, diagnosis_info)


__all__ = ["generate_recommendation_reason"]


