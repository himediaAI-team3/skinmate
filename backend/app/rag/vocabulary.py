"""Vocabulary 로더 (캐시 포함)"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


_VOCAB_CACHE: Dict[str, int] | None = None


def load_vocabulary() -> Dict[str, int]:
    global _VOCAB_CACHE
    if _VOCAB_CACHE is not None:
        return _VOCAB_CACHE

    # backend/data/vocabulary.json 경로 추론
    project_root = Path(__file__).parent.parent.parent  # backend
    vocab_path = project_root / "data" / "vocabulary.json"
    if not vocab_path.exists():
        # 빈 사전이라도 반환 (운영 안전)
        _VOCAB_CACHE = {}
        return _VOCAB_CACHE

    with vocab_path.open("r", encoding="utf-8") as f:
        _VOCAB_CACHE = json.load(f)
    return _VOCAB_CACHE


