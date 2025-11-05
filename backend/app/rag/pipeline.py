from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from sqlalchemy.orm import Session

from app.rag.data_loader import load_diagnosis_info
from app.rag.query_generator import generate_search_query
from app.rag.retriever import get_ensemble_retriever
from app.rag.reranker import rerank_documents
from app.rag.reason_generator import generate_recommendation_reason
from app.schemas.rag import DiagnosisInfo, QuerySpec, RecommendationItem, PriceFilter
from app.core.config.logging import get_logger
logger = get_logger(__name__)


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        # try parse from string
        return float(str(value))
    except Exception:
        return None


def apply_price_filter(state: Dict[str, Any]) -> Dict[str, Any]:
    """Filter documents by price based on query_spec or diagnosis_info.

    Priority: query_spec.price_filter -> diagnosis_info(min/max)
    """
    diagnosis_info: Dict[str, Any] = state["diagnosis_info"]
    documents: List[Document] = state["documents"]

    # Prefer query_spec filter
    min_price = None
    max_price = None
    qspec = state.get("query_spec")
    if isinstance(qspec, QuerySpec):
        if isinstance(qspec.price_filter, PriceFilter):
            min_price = qspec.price_filter.gte
            max_price = qspec.price_filter.lte
    else:
        qpf = (qspec or {}).get("price_filter") if isinstance(qspec, dict) else None
        if isinstance(qpf, dict):
            min_price = qpf.get("gte")
            max_price = qpf.get("lte")

    # Fallback to diagnosis_info
    if min_price is None and max_price is None:
        min_price = diagnosis_info.get("min_price")
        max_price = diagnosis_info.get("max_price")

    min_v = _to_float(min_price)
    max_v = _to_float(max_price)

    if min_v is None and max_v is None:
        return state

    filtered: List[Document] = []
    for doc in documents:
        p = _to_float((doc.metadata or {}).get("price"))
        if p is None:
            filtered.append(doc)  # keep when price unknown
            continue
        ok = True
        if min_v is not None and p < min_v:
            ok = False
        if max_v is not None and p > max_v:
            ok = False
        if ok:
            filtered.append(doc)

    return {**state, "documents": filtered}


def _load_info(x: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "diagnosis_info": load_diagnosis_info(x["db"], x["analysis_id"]),
        "analysis_id": x["analysis_id"],
        "db": x["db"],
    }


def _apply_query(x: Dict[str, Any]) -> Dict[str, Any]:
    diag = x["diagnosis_info"]
    diag_model = diag if isinstance(diag, DiagnosisInfo) else DiagnosisInfo.model_validate(diag)
    return {**x, "query_spec": generate_search_query(diag_model)}


def _run_search(x: Dict[str, Any]) -> Dict[str, Any]:
    retriever = get_ensemble_retriever(k=10)
    qspec = x.get("query_spec")
    if isinstance(qspec, QuerySpec):
        query_text = qspec.text_query
    else:
        query_text = (qspec or {}).get("text_query") if isinstance(qspec, dict) else None
    docs = retriever.invoke(query_text) if query_text else []
    return {**x, "documents": docs}


def _apply_rerank(x: Dict[str, Any]) -> Dict[str, Any]:
    top3 = rerank_documents(x.get("documents") or [], x["diagnosis_info"], top_k=3)
    return {**x, "top3": top3}


def _generate_reasons_for_all(state: Dict[str, Any]) -> Dict[str, Any]:
    top3: List[Document] = state.get("top3") or []
    diagnosis_info: Dict[str, Any] = state["diagnosis_info"]
    # LCEL map으로 병렬 실행
    inputs = [
        {"rank": rank, "doc": doc, "diagnosis": diagnosis_info}
        for rank, doc in enumerate(top3, start=1)
    ]

    def _reason_lambda(x: Dict[str, Any]) -> Dict[str, Any]:
        rank = x["rank"]
        doc = x["doc"]
        diagnosis = x["diagnosis"]
        reason = generate_recommendation_reason(doc, diagnosis, rank)
        md = doc.metadata or {}
        cid = md.get("cosmetic_id")
        return {"rank": rank, "cosmetic_id": cid, "reason": reason}

    reason_map = RunnableLambda(_reason_lambda).map().with_config(run_name="reason_generation_map", max_concurrency=3)
    results: List[Dict[str, Any]] = reason_map.invoke(inputs) if inputs else []

    items: List[RecommendationItem] = []
    for r in results:
        try:
            cid_int = int(r.get("cosmetic_id"))
        except Exception:
            continue
        items.append(RecommendationItem(cosmetic_id=cid_int, ranking=int(r.get("rank", 0)), reason=r.get("reason") or ""))

    items.sort(key=lambda x: x.ranking)
    logger.info(f"reason_generation_all (LCEL map) produced {len(items)} items")
    return {**state, "recommendations": items}


def _format_recommendations(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"analysis_id": state["analysis_id"], "recommendations": state.get("recommendations") or []}


def create_rag_pipeline() -> Runnable:
    pipeline: Runnable = (
        RunnablePassthrough().with_config(run_name="rag_pipeline_input")
        | RunnableLambda(_load_info).with_config(run_name="load_diagnosis")
        | RunnableLambda(_apply_query).with_config(run_name="query_generation")
        | RunnableLambda(_run_search).with_config(run_name="search")
        | RunnableLambda(apply_price_filter).with_config(run_name="price_filter")
        | RunnableLambda(_apply_rerank).with_config(run_name="reranking")
        | RunnableLambda(_generate_reasons_for_all).with_config(run_name="reason_generation_all")
        | RunnableLambda(_format_recommendations).with_config(run_name="format_result")
    ).with_config(run_name="rag_pipeline")
    return pipeline


def recommend_products(db: Session, analysis_id: int) -> List[RecommendationItem]:
    """Run the RAG pipeline and return recommendations as list of RecommendationItem."""
    pipeline = create_rag_pipeline()
    result: Dict[str, Any] = pipeline.invoke({"analysis_id": analysis_id, "db": db})
    recs = result.get("recommendations") or []
    # Ensure type
    if recs and isinstance(recs[0], RecommendationItem):
        return recs
    return [RecommendationItem.model_validate(r) for r in recs]


__all__ = [
    "create_rag_pipeline",
    "recommend_products",
    "apply_price_filter",
]


