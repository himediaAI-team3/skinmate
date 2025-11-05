from __future__ import annotations

import re
from typing import Dict, List, Optional

from langchain_core.documents import Document
from app.rag.constants import DISEASE_SYNONYMS, COMPATIBLE_SKIN_TYPES


_DISEASE_SYNONYMS = DISEASE_SYNONYMS
_COMPATIBLE_SKIN_TYPES = COMPATIBLE_SKIN_TYPES


def _contains_any(text: str, candidates: List[str]) -> bool:
    low = text.lower()
    return any(c.lower() in low for c in candidates)


def _extract_skin_type_from_text(text: str) -> Optional[str]:
    # Simple keyword-based extraction
    for st in {"건성", "지성", "복합성", "민감성", "중성"}:
        if st in text:
            return st
    # common phrases like "건성 피부", "지성 피부"
    m = re.search(r"(건성|지성|복합성|민감성|중성)\s*피부", text)
    if m:
        return m.group(1)
    return None


def _disease_matches(doc: Document, disease_name: str) -> bool:
    if not disease_name:
        return False
    synonyms = _DISEASE_SYNONYMS.get(disease_name, [disease_name])

    # Prefer metadata
    meta_val = (doc.metadata or {}).get("skin_disease")
    if isinstance(meta_val, str) and meta_val:
        if _contains_any(meta_val, synonyms):
            return True

    # Fallback to content
    return _contains_any(doc.page_content or "", synonyms)


def _skin_type_score(doc: Document, user_skin_type: Optional[str]) -> float:
    if not user_skin_type:
        return 0.0

    user_skin_type = user_skin_type.strip()
    compat_list = _COMPATIBLE_SKIN_TYPES.get(user_skin_type, [user_skin_type])

    # Prefer metadata
    meta_val = (doc.metadata or {}).get("skin_type")
    doc_skin = None
    if isinstance(meta_val, str) and meta_val:
        doc_skin = meta_val
    else:
        doc_skin = _extract_skin_type_from_text(doc.page_content or "")

    if not doc_skin:
        return 0.0

    if doc_skin == user_skin_type:
        return 0.1
    if doc_skin in compat_list:
        return 0.05
    return 0.0


def rerank_documents(
    documents: List[Document],
    diagnosis_info: Dict[str, Optional[object]],
    top_k: int = 3,
) -> List[Document]:
    """Rerank retrieved documents using custom scoring rules.

    Args:
        documents (List[Document]): Retrieved documents (about 20).
        diagnosis_info (Dict[str, Optional[object]]): Contains disease_name, skin_type.
        top_k (int): Number of top documents to return.

    Returns:
        List[Document]: Top-k reranked documents with metadata['rerank_score'] set.
    """

    if not documents:
        return []

    disease_name = str(diagnosis_info.get("disease_name") or "")
    user_skin_type = diagnosis_info.get("skin_type")  # Optional[str]

    scored: List[Document] = []
    for rank, doc in enumerate(documents):
        base = 1.0 / (rank + 60.0)

        score = base

        # disease boost
        if _disease_matches(doc, disease_name):
            score += 0.1

        # skin-type compatibility
        score += _skin_type_score(doc, user_skin_type if isinstance(user_skin_type, str) else None)

        # attach for debugging
        if doc.metadata is None:
            doc.metadata = {}
        doc.metadata["rerank_score"] = float(score)

        scored.append(doc)

    scored.sort(key=lambda d: d.metadata.get("rerank_score", 0.0), reverse=True)
    return scored[: max(top_k, 0)]


__all__ = ["rerank_documents"]


