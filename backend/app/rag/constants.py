from __future__ import annotations

from typing import Dict, List


# 질환 동의어 사전 (리랭킹·키워드 매칭 공통 사용)
DISEASE_SYNONYMS: Dict[str, List[str]] = {
    "아토피": ["아토피", "아토피 피부염", "atopic dermatitis"],
    "여드름": ["여드름", "acne"],
    "주사": ["주사", "rosacea"],
    "지루": ["지루", "지루피부염", "seborrheic dermatitis"],
    "건선": ["건선", "psoriasis"],
    "정상": ["정상"],
}


# 피부타입 호환 규칙
COMPATIBLE_SKIN_TYPES: Dict[str, List[str]] = {
    "건성": ["건성", "중건성", "민감성"],
    "지성": ["지성", "복합성", "민감성"],
    "복합성": ["복합성", "지성", "건성"],
    "민감성": ["민감성", "건성", "복합성"],
}


# 메타데이터 키 (권장 스키마)
METADATA_KEYS = {
    "cosmetic_id",
    "name",
    "brand",
    "category",
    "price",
    "skin_type",
    "skin_disease",
}


__all__ = [
    "DISEASE_SYNONYMS",
    "COMPATIBLE_SKIN_TYPES",
    "METADATA_KEYS",
]


