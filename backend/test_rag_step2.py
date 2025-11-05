"""Quick test script for RAG Step 2 components."""

from app.rag import (
    load_diagnosis_info,
    generate_search_query,
    get_ensemble_retriever,
    rerank_documents,
)
from app.core.config.database import SessionLocal

# Test with a sample analysis_id
db = SessionLocal()
try:
    analysis_id = 1  # Change this to your test ID
    
    print(f"[1/4] Loading diagnosis info for analysis_id={analysis_id}...")
    info = load_diagnosis_info(db, analysis_id)
    print(f"      ✓ Loaded: {info['disease_name']}, skin_type={info['skin_type']}")
    
    print(f"[2/4] Generating search query...")
    query_spec = generate_search_query(info)
    print(f"      ✓ Query: {query_spec['text_query'][:50]}...")
    print(f"      ✓ Keywords: {query_spec['keywords']}")
    
    print(f"[3/4] Searching with EnsembleRetriever...")
    retriever = get_ensemble_retriever(k=20)
    docs = retriever.invoke(query_spec["text_query"])
    print(f"      ✓ Found {len(docs)} documents")
    
    print(f"[4/4] Reranking top 3...")
    top3 = rerank_documents(docs, info, top_k=3)
    print(f"      ✓ Top 3:")
    for i, doc in enumerate(top3, 1):
        score = doc.metadata.get("rerank_score", 0.0)
        brand = doc.metadata.get("brand", "N/A")
        price = doc.metadata.get("price", "N/A")
        print(f"        {i}. {brand} - ₩{price:,} (score: {score:.3f})")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

