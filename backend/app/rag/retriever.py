"""Retrievers for RAG (Dense, BM25, Ensemble).

Provides factory functions returning retrievers with simple singleton caching.
BM25 documents are prebuilt and stored as a pickle file by
`backend/scripts/prepare_bm25_documents.py`.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.core.config.qdrant import get_vector_store


# Caches per k to respect different top-k settings without re-instantiation.
_DENSE_CACHE: Dict[int, object] = {}
_BM25_CACHE: Dict[int, BM25Retriever] = {}
_ENSEMBLE_CACHE: Dict[int, EnsembleRetriever] = {}


def _bm25_pickle_path() -> Path:
    """Return absolute path to the BM25 pickle file under backend/scripts.

    Returns:
        Path: Absolute file path to bm25_documents.pkl
    """
    # This file is at backend/app/rag/retriever.py
    # Move up two levels to backend/, then into scripts/
    return Path(__file__).resolve().parents[2] / "scripts" / "bm25_documents.pkl"


def get_dense_retriever(k: int = 20):
    """Return a dense retriever from Qdrant VectorStore.

    Args:
        k (int): Number of top results to retrieve.

    Returns:
        BaseRetriever: LangChain retriever wrapping Qdrant vector store.
    """
    if k in _DENSE_CACHE:
        return _DENSE_CACHE[k]

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    _DENSE_CACHE[k] = retriever
    return retriever


def get_bm25_retriever(k: int = 20) -> BM25Retriever:
    """Return a BM25 retriever built from precomputed documents.

    Args:
        k (int): Number of top results to retrieve.

    Returns:
        BM25Retriever: BM25-based keyword retriever.

    Raises:
        FileNotFoundError: If bm25_documents.pkl file is missing.
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
    """Return an ensemble retriever combining dense and BM25.

    Args:
        k (int): Number of top results to retrieve for each retriever.

    Returns:
        EnsembleRetriever: Ensemble with reciprocal rank fusion.
    """
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


__all__ = [
    "get_dense_retriever",
    "get_bm25_retriever",
    "get_ensemble_retriever",
]


