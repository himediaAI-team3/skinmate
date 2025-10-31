"""
Step 4: 검색 테스트
실행: python scripts/rag/4_test_search.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
from qdrant_client.models import Filter, FieldCondition, Range, NamedVector, NamedSparseVector
from app.core.config.qdrant import qdrant_client, QdrantConfig
from app.core.config.embedding import embedding_model
from app.rag.vector_builder import create_search_sparse_vector

def test_search():
    print("=" * 60)
    print("Step 4: 검색 테스트")
    print("=" * 60)
    
    # Vocabulary 로드
    vocab_path = project_root / 'data' / 'vocabulary.json'
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocabulary = json.load(f)
    
    # 테스트 쿼리
    print("\n🔍 테스트 쿼리: 아토피 피부 보습 제품 (2~5만원)")
    
    # Dense 쿼리
    query_text = "아토피 피부의 건조와 홍조를 진정시키고 보습하는 크림"
    dense_query = embedding_model.encode(query_text).tolist()
    
    # Sparse 쿼리
    keywords = ["건조", "홍조", "보습", "진정", "피부장벽강화"]
    sparse_query = create_search_sparse_vector(keywords, vocabulary)
    
    # 필터
    filters = Filter(
        must=[
            FieldCondition(
                key="price",
                range=Range(gte=20000, lte=50000)
            )
        ],
        should=[
            FieldCondition(key="skin_disease", match={"value": "아토피"})
        ]
    )
    
    # 검색 실행
    print("\n검색 중...")
    # 최신 클라이언트: 각각 검색 후 RRF 수동 결합
    res_dense = qdrant_client.search(
        collection_name=QdrantConfig.COLLECTION_NAME,
        query_vector=NamedVector(name="dense", vector=dense_query),
        limit=20,
        with_payload=True,
        query_filter=filters,
    )
    res_sparse = qdrant_client.search(
        collection_name=QdrantConfig.COLLECTION_NAME,
        query_vector=NamedSparseVector(name="sparse", vector=sparse_query),
        limit=20,
        with_payload=True,
        query_filter=filters,
    )

    from collections import defaultdict
    rrf_scores = defaultdict(float)
    
    def add_rrf(results):
        for i, p in enumerate(results, start=1):
            rrf_scores[p.id] += 1.0 / (60 + i)

    add_rrf(res_dense)
    add_rrf(res_sparse)

    payload_map = {}
    for p in list(res_dense) + list(res_sparse):
        payload_map[p.id] = p.payload

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    # 결과 출력
    print("\n" + "=" * 60)
    print("검색 결과 (Top 5)")
    print("=" * 60)

    for idx, (pid, score) in enumerate(ranked, 1):
        payload = payload_map.get(pid, {})
        print(f"\n{idx}. {payload.get('name')}")
        print(f"   브랜드: {payload.get('brand')}")
        print(f"   가격: {float(payload.get('price', 0)) :,.0f}원")
        print(f"   효능: {payload.get('main_effect')}")
        print(f"   증상: {payload.get('care_symptom')}")
    
    print("\n✅ Step 4 완료!")

if __name__ == "__main__":
    test_search()