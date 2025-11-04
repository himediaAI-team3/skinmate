"""Qdrant configuration (singleton).

Provides singleton helpers for Qdrant client and LangChain QdrantVectorStore
that attaches to an existing collection.

Environment Variables:
    - QDRANT_URL: Base URL of Qdrant service.
    - QDRANT_API_KEY: API key for Qdrant (if auth is enabled).
    - QDRANT_COLLECTION_NAME: Existing collection name (default: "cosmetics").
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

try:
    from langchain_qdrant import QdrantVectorStore  # type: ignore
except Exception:  # pragma: no cover - fallback
    try:
        from langchain_qdrant import Qdrant as QdrantVectorStore  # type: ignore
    except Exception:  # pragma: no cover - last resort
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
    """Return a singleton QdrantClient.

    Returns:
        QdrantClient: Qdrant client instance.

    Raises:
        EnvironmentError: If required env variables are missing.
        RuntimeError: If connection initialization fails.
    """
    global _QDRANT_CLIENT_SINGLETON
    if _QDRANT_CLIENT_SINGLETON is not None:
        return _QDRANT_CLIENT_SINGLETON

    url = _require_env("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    try:
        _QDRANT_CLIENT_SINGLETON = QdrantClient(url=url, api_key=api_key)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Qdrant 클라이언트 초기화에 실패했습니다. URL/API Key를 확인하세요."
        ) from exc

    return _QDRANT_CLIENT_SINGLETON


def get_vector_store() -> QdrantVectorStore:
    """Return a singleton QdrantVectorStore bound to an existing collection.

    Returns:
        QdrantVectorStore: Vector store for the existing collection.

    Raises:
        EnvironmentError: If required env variables are missing.
        RuntimeError: If vector store initialization fails.
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
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            (
                "Qdrant 벡터 스토어 연결에 실패했습니다.\n"
                f"URL: {url}, Collection: {collection}\n"
                "컬렉션이 생성되어 있는지 확인하세요."
            )
        ) from exc

    return _VECTOR_STORE_SINGLETON


__all__ = ["get_qdrant_client", "get_vector_store"]


