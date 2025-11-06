"""Qdrant 설정 (싱글톤).

기존 컬렉션에 연결하는 Qdrant 클라이언트와 LangChain QdrantVectorStore 싱글톤을 제공합니다.

환경 변수:
    - QDRANT_URL: Qdrant 서비스 기본 URL
    - QDRANT_API_KEY: Qdrant API 키 (인증이 활성화된 경우)
    - QDRANT_COLLECTION_NAME: 컬렉션 이름 (기본값: "cosmetics")
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

try:
    from langchain_qdrant import QdrantVectorStore  # type: ignore
except Exception:
    try:
        from langchain_qdrant import Qdrant as QdrantVectorStore  # type: ignore
    except Exception:
        from langchain_community.vectorstores import Qdrant as QdrantVectorStore  # type: ignore

from qdrant_client import QdrantClient

from app.core.config.embedding import get_embeddings


load_dotenv()

_QDRANT_CLIENT_SINGLETON: Optional[QdrantClient] = None
_VECTOR_STORE_SINGLETON: Optional[QdrantVectorStore] = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"환경 변수가 누락되었습니다: {name}")
    return value


def get_qdrant_client() -> QdrantClient:
    """QdrantClient 싱글톤을 반환합니다.

    Returns:
        QdrantClient: Qdrant 클라이언트 인스턴스

    Raises:
        EnvironmentError: 필수 환경 변수가 없을 때
        RuntimeError: 연결 초기화 실패 시
    """
    global _QDRANT_CLIENT_SINGLETON
    if _QDRANT_CLIENT_SINGLETON is not None:
        return _QDRANT_CLIENT_SINGLETON

    url = _require_env("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    try:
        _QDRANT_CLIENT_SINGLETON = QdrantClient(url=url, api_key=api_key)
    except Exception as exc:
        raise RuntimeError(
            "Qdrant 클라이언트 초기화에 실패했습니다. URL/API Key를 확인하세요."
        ) from exc

    return _QDRANT_CLIENT_SINGLETON


def get_vector_store() -> QdrantVectorStore:
    """기존 컬렉션에 연결된 QdrantVectorStore 싱글톤을 반환합니다.

    Returns:
        QdrantVectorStore: 기존 컬렉션용 벡터 스토어

    Raises:
        EnvironmentError: 필수 환경 변수가 없을 때
        RuntimeError: 벡터 스토어 초기화 실패 시
    """
    global _VECTOR_STORE_SINGLETON
    if _VECTOR_STORE_SINGLETON is not None:
        return _VECTOR_STORE_SINGLETON

    url = _require_env("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection = os.getenv("QDRANT_COLLECTION_NAME", "cosmetics")

    embeddings = get_embeddings()

    try:
        client = get_qdrant_client()

        _VECTOR_STORE_SINGLETON = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            url=url,
            api_key=api_key,
            collection_name=collection,
        )
    except Exception as exc:
        raise RuntimeError(
            (
                "Qdrant 벡터 스토어 연결에 실패했습니다.\n"
                f"URL: {url}, Collection: {collection}\n"
                "컬렉션이 생성되어 있는지 확인하세요."
            )
        ) from exc

    return _VECTOR_STORE_SINGLETON


__all__ = ["get_qdrant_client", "get_vector_store"]


