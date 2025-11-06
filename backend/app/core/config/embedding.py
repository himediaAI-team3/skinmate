"""임베딩 설정 (싱글톤).

HuggingFaceEmbeddings 싱글톤 인스턴스를 제공하여 반복 초기화 오버헤드를 방지합니다.

환경 변수:
    - EMBEDDING_MODEL: HuggingFace 모델 ID (기본값: "jhgan/ko-sroberta-multitask")
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception as exc:
    raise ImportError(
        "langchain-huggingface 패키지가 필요합니다. requirements.txt를 설치하세요."
    ) from exc


load_dotenv()

_EMBEDDINGS_SINGLETON: Optional[HuggingFaceEmbeddings] = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """HuggingFaceEmbeddings 싱글톤 인스턴스를 반환합니다.

    Returns:
        HuggingFaceEmbeddings: 캐시된 임베딩 인스턴스

    Raises:
        RuntimeError: 임베딩 모델 로드 실패 시
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
    except Exception as exc:
        raise RuntimeError(
            (
                "임베딩 모델 로드에 실패했습니다. 모델: {model}\n"
                "- EMBEDDING_MODEL 환경 변수를 확인하세요.\n"
                "- sentence-transformers 모델 다운로드 가능 여부를 확인하세요."
            ).format(model=model_name)
        ) from exc

    return _EMBEDDINGS_SINGLETON


__all__ = ["get_embeddings"]


