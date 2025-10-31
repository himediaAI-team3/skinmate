"""진단 정보를 검색 쿼리로 변환하는 유틸리티"""
from __future__ import annotations

import json
from typing import Dict, List, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config.openai import llm_client


class QuerySpec(TypedDict, total=False):
    dense_text: str
    keywords: List[str]
    must_keywords: List[str]
    avoid_ingredients: List[str]
    notes: str


# 질환 → 효능/성분 브리지(초안)
DISEASE_TO_EFFECTS: Dict[str, Dict[str, List[str]]] = {
    "아토피": {
        "keywords": ["보습", "진정", "피부장벽강화", "가려움완화"],
        "ingredients": ["세라마이드", "판테놀", "시어버터", "히알루론산"],
    },
    "여드름": {
        "keywords": ["피지조절", "모공케어", "각질용해", "진정"],
        "ingredients": ["살리실산", "나이아신아마이드", "아젤라익산"],
    },
    "주사": {
        "keywords": ["홍조진정", "진정", "자극완화", "피부장벽강화"],
        "ingredients": ["아줄렌", "알란토인", "마데카소사이드"],
    },
    "지루": {
        "keywords": ["피지조절", "각질케어", "진정"],
        "ingredients": ["징크피씨에이", "살리실산"],
    },
    "건선": {
        "keywords": ["각질완화", "진정", "보습"],
        "ingredients": ["우레아", "판테놀", "세라마이드"],
    },
    "정상": {
        "keywords": ["보습", "기초케어", "저자극"],
        "ingredients": ["히알루론산", "글리세린"],
    },
}


SYSTEM_PROMPT = (
    "당신은 스킨케어 추천을 위한 검색 질의 생성기입니다. "
    "입력으로 질병명과 요약(summary)을 받으면, 화장품의 효능/성분 기반 검색에 최적인 질의를 JSON으로 생성하세요. "
    "키는 반드시 dense_text, keywords, must_keywords, avoid_ingredients, notes 를 포함합니다. "
    "출력은 JSON만 반환하세요. 추가 설명이나 마크다운은 금지합니다."
)


def _fallback_query(disease: str, summary: str) -> QuerySpec:
    bridge = DISEASE_TO_EFFECTS.get(disease, {"keywords": ["보습"], "ingredients": []})
    keywords = bridge.get("keywords", [])
    dense = f"{disease}로 인한 증상을 완화하기 위한 {','.join(keywords[:2])} 중심의 저자극 케어 제품"
    return QuerySpec(
        dense_text=dense,
        keywords=keywords,
        must_keywords=keywords[:1] if keywords else [],
        avoid_ingredients=["강한 향료"],
        notes="rule-based fallback",
    )


def generate_query_from_diagnosis(disease: str, summary: str) -> QuerySpec:
    """진단 정보를 바탕으로 LLM을 사용해 검색 쿼리를 생성한다."""
    # 브리지 힌트 문자열
    bridge = DISEASE_TO_EFFECTS.get(disease, {"keywords": [], "ingredients": []})
    bridge_hint = {
        "disease": disease,
        "suggested_keywords": bridge.get("keywords", []),
        "suggested_ingredients": bridge.get("ingredients", []),
    }

    user_content = {
        "disease": disease,
        "summary": summary,
        "hint": bridge_hint,
        "constraints": {
            "language": "ko",
            "keyword_style": "명사형, vocabulary에 존재 가능성이 높은 한국어 단어 위주",
        },
    }

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(user_content, ensure_ascii=False)),
        ]
        resp = llm_client.invoke(messages)
        text = resp.content if isinstance(resp.content, str) else str(resp.content)
        data = json.loads(text)

        # 최소 키 보정
        if not isinstance(data, dict):
            return _fallback_query(disease, summary)

        dense_text = data.get("dense_text") or _fallback_query(disease, summary)["dense_text"]
        keywords = data.get("keywords") or bridge.get("keywords", [])
        must_keywords = data.get("must_keywords") or (keywords[:1] if keywords else [])
        avoid_ingredients = data.get("avoid_ingredients") or ["강한 향료"]
        notes = data.get("notes") or ""

        return QuerySpec(
            dense_text=dense_text,
            keywords=keywords,
            must_keywords=must_keywords,
            avoid_ingredients=avoid_ingredients,
            notes=notes,
        )
    except Exception:
        return _fallback_query(disease, summary)


