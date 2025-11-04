"""Embedding configuration (singleton).

Provides a singleton instance of HuggingFaceEmbeddings to avoid repeated
initialization overhead.

Environment Variables:
    - EMBEDDING_MODEL: HuggingFace model id (default: "jhgan/ko-sroberta-multitask").

This module is intentionally lightweight and CPU-friendly by default.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception as exc:  # pragma: no cover - Import-time guard
    raise ImportError(
        "langchain-huggingface 패키지가 필요합니다. requirements.txt를 설치하세요."
    ) from exc


load_dotenv()

_EMBEDDINGS_SINGLETON: Optional[HuggingFaceEmbeddings] = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a singleton HuggingFaceEmbeddings instance.

    Returns:
        HuggingFaceEmbeddings: A cached embeddings instance.

    Raises:
        RuntimeError: If the embedding model fails to load.
    """
    global _EMBEDDINGS_SINGLETON
    if _EMBEDDINGS_SINGLETON is not None:
        return _EMBEDDINGS_SINGLETON

    model_name = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")

    try:
        _EMBEDDINGS_SINGLETON = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception as exc:  # pragma: no cover - model init error path
        raise RuntimeError(
            (
                "임베딩 모델 로드에 실패했습니다. 모델: {model}\n"
                "- EMBEDDING_MODEL 환경 변수를 확인하세요.\n"
                "- sentence-transformers 모델 다운로드 가능 여부를 확인하세요."
            ).format(model=model_name)
        ) from exc

    return _EMBEDDINGS_SINGLETON


__all__ = ["get_embeddings"]


