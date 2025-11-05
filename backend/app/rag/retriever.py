"""RAG 검색기 모음(Dense, BM25, Ensemble).

간단한 캐시를 사용해 재생성을 줄입니다.
BM25 문서는 사전 구축되어 `scripts/prepare_bm25_documents.py`로 생성합니다.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.core.config.qdrant import get_vector_store, get_qdrant_client
from app.core.config.embedding import get_embeddings

# QdrantVectorStore import (qdrant.py와 동일한 방식)
try:
    from langchain_qdrant import QdrantVectorStore  # type: ignore
except Exception:  # pragma: no cover - fallback
    try:
        from langchain_qdrant import Qdrant as QdrantVectorStore  # type: ignore
    except Exception:  # pragma: no cover - last resort
        from langchain_community.vectorstores import Qdrant as QdrantVectorStore  # type: ignore


# 검색 k 값 별로 인스턴스를 캐시합니다.
_DENSE_CACHE: Dict[int, object] = {}
_BM25_CACHE: Dict[int, BM25Retriever] = {}
_ENSEMBLE_CACHE: Dict[int, EnsembleRetriever] = {}
_ENSEMBLE_FILTER_CACHE: Dict[tuple[int, str], EnsembleRetriever] = {}


def _bm25_pickle_path() -> Path:
    """BM25 문서 피클 파일 경로를 반환합니다."""
    return Path(__file__).resolve().parents[2] / "scripts" / "bm25_documents.pkl"


def get_dense_retriever(k: int = 20):
    """Qdrant 기반 벡터 리트리버를 반환합니다."""
    if k in _DENSE_CACHE:
        return _DENSE_CACHE[k]

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    _DENSE_CACHE[k] = retriever
    return retriever


def get_bm25_retriever(k: int = 20) -> BM25Retriever:
    """사전 구축된 문서로 BM25 리트리버를 생성합니다.

    파일이 없으면 FileNotFoundError를 발생시킵니다.
    """
    if k in _BM25_CACHE:
        return _BM25_CACHE[k]

    path = _bm25_pickle_path()
    if not path.exists():
        raise FileNotFoundError(
            (
                f"BM25용 Document 파일이 없습니다: {path}\n"
                "먼저 'python scripts/prepare_bm25_documents.py' 실행하세요."
            )
        )

    with path.open("rb") as f:
        documents: list[Document] = pickle.load(f)

    retriever = BM25Retriever.from_documents(documents, k=k)
    _BM25_CACHE[k] = retriever
    return retriever


def get_ensemble_retriever(k: int = 20) -> EnsembleRetriever:
    """Dense와 BM25를 결합한 앙상블 리트리버를 반환합니다."""
    if k in _ENSEMBLE_CACHE:
        return _ENSEMBLE_CACHE[k]

    dense = get_dense_retriever(k)
    bm25 = get_bm25_retriever(k)

    ensemble = EnsembleRetriever(
        retrievers=[dense, bm25],
        weights=[0.5, 0.5],
    )
    _ENSEMBLE_CACHE[k] = ensemble
    return ensemble


def get_ensemble_retriever_with_filter(k: int, payload_filter: dict) -> EnsembleRetriever:
    """Qdrant payload filter를 적용한 Dense + BM25 앙상블을 생성합니다.

    LangChain QdrantVectorStore 표준 retriever를 사용하고, filter를 그대로 전달합니다.
    """
    import os
    import json as _json

    try:
        filter_key = _json.dumps(payload_filter, sort_keys=True, ensure_ascii=True)
    except Exception:
        filter_key = str(payload_filter)
    cache_key = (k, filter_key)
    if cache_key in _ENSEMBLE_FILTER_CACHE:
        return _ENSEMBLE_FILTER_CACHE[cache_key]

    # get_vector_store()와 동일한 방식으로 생성
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "cosmetics")
    
    if not url:
        raise EnvironmentError("QDRANT_URL 환경 변수가 필요합니다.")

    dense_vs = QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        url=url,
        api_key=api_key,
        collection_name=collection_name,
    )
    dense = dense_vs.as_retriever(search_kwargs={"k": k, "filter": payload_filter})
    bm25 = get_bm25_retriever(k)

    ensemble = EnsembleRetriever(
        retrievers=[dense, bm25],
        weights=[0.5, 0.5],
    )
    _ENSEMBLE_FILTER_CACHE[cache_key] = ensemble
    return ensemble


__all__ = [
    "get_dense_retriever",
    "get_bm25_retriever",
    "get_ensemble_retriever",
    "get_ensemble_retriever_with_filter",
]


