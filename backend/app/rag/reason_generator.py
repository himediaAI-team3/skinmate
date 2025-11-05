from __future__ import annotations

from typing import Any, Dict

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.config.openai import get_llm


SYSTEM_PROMPT = (
    "당신은 화장품 추천 전문가입니다.\n"
    "고객에게 이 제품을 추천하는 이유를 제품의 고유한 특성 중심으로 200자 이내로 작성하세요.\n\n"
    "## 작성 원칙\n"
    "1. 제품의 특징과 효능을 먼저 언급 (질환 설명은 최소화)\n"
    "2. 브랜드/제품의 특별한 점 강조\n"
    "3. 200자 엄수\n"
    "4. 자연스러운 문장 구조\n"
    "5. 순위별로 다양한 표현 사용\n\n"
    "## 나쁜 예시\n"
    "- '아토피의 핵심은...' (질환 설명으로 시작 - 피해야 함)\n"
    "- '케어에 적합한 제품입니다' (너무 일반적)\n"
)


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
                    "브랜드: {brand}\n카테고리: {category}\n가격: {price}원\n"
                    "고객 정보:\n질환: {disease_name}\n피부타입: {skin_type}\n순위: {rank}위\n\n"
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
                "category": md.get("category") or "",
                "price": md.get("price") or 0,
                "disease_name": diagnosis_info.get("disease_name") or "",
                "skin_type": diagnosis_info.get("skin_type") or "",
                "rank": rank,
            }
        )
        return _truncate_200(text or "")
    except Exception:
        return _fallback_reason(product, diagnosis_info)


__all__ = ["generate_recommendation_reason"]


