from __future__ import annotations

from typing import Any, Dict

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm
from app.utils.prompt import load_prompt


SYSTEM_PROMPT = load_prompt("reason_generation.yaml")


def _truncate_170(text: str) -> str:
    if len(text) <= 170:
        return text
    return text[:167] + "..."


def _fallback_reason(product: Document, diagnosis_info: Dict[str, Any]) -> str:
    brand = (product.metadata or {}).get("brand") or "이"
    disease = (diagnosis_info.get("disease_name") or "피부")
    return _truncate_170(f"{brand} 제품은 {disease} 케어에 효과적입니다.")


def _build_chain() -> Runnable:
    llm = get_llm(temperature=0.5, max_tokens=150, timeout=10)
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
                    "추천 이유를 170자 이내로 작성하세요."
                ),
            ),
        ]
    )
    chain: Runnable = (prompt | llm | StrOutputParser()).with_config(run_name="reason_generation")
    return chain


def generate_recommendation_reason(product: Document, diagnosis_info: Dict[str, Any], rank: int) -> str:
    """지정 제품에 대한 간단한 추천 이유를 생성합니다.

    Args:
        product (Document): 제품 문서(메타데이터/내용 포함)
        diagnosis_info (Dict[str, Any]): 질환/피부타입 등 사용자 컨텍스트
        rank (int): 순위(1..3)

    Returns:
        str: 170자 이내 추천 이유(실패 시 안전한 폴백)
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
        return _truncate_170(text or "")
    except Exception:
        return _fallback_reason(product, diagnosis_info)


__all__ = ["generate_recommendation_reason"]


