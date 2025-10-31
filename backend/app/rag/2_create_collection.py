"""
Step 2: Qdrant 컬렉션 생성
실행: python scripts/rag/2_create_collection.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config.qdrant import qdrant_client, QdrantConfig
from app.core.config.embedding import EmbeddingConfig
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, PayloadSchemaType

def create_collection():
    print("=" * 60)
    print("Step 2: Qdrant 컬렉션 생성 및 인덱스 설정")
    print("=" * 60)
    
    collection_name = QdrantConfig.COLLECTION_NAME
    
    # 기존 컬렉션 확인
    print(f"\n[1/4] 기존 '{collection_name}' 컬렉션 확인 중...")
    collection_exists = False
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        collection_exists = True
        print(f"      → 기존 컬렉션 존재 (포인트 수: {collection_info.points_count})")
    except Exception:
        print(f"      → 기존 컬렉션 없음")
    
    # 컬렉션 생성 (없을 경우)
    if not collection_exists:
        print(f"[2/4] 새 컬렉션 생성 중...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=EmbeddingConfig.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams()
            }
        )
        print(f"      → '{collection_name}' 컬렉션 생성 완료")
    else:
        print(f"[2/4] 기존 컬렉션 사용 (스킵)")
    
    # 가격 필터링을 위한 인덱스 생성
    print(f"[3/4] price 필드 인덱스 생성 중...")
    try:
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="price",
            field_schema=PayloadSchemaType.FLOAT,
        )
        print(f"      → price 인덱스 생성 완료")
    except Exception as e:
        error_str = str(e).lower()
        if "already exists" in error_str or "이미" in error_str:
            print(f"      → 인덱스가 이미 존재합니다 (정상)")
        else:
            print(f"      → 인덱스 생성 실패: {e}")
    
    # 컬렉션 정보 확인
    print(f"[4/4] 컬렉션 정보 확인 중...")
    collection_info = qdrant_client.get_collection(collection_name)
    print(f"      → Dense Vector 차원: {EmbeddingConfig.VECTOR_SIZE}")
    print(f"      → Sparse Vector 지원: 활성화")
    print(f"      → 거리 측정: COSINE")
    print(f"      → 포인트 수: {collection_info.points_count}")
    
    print("\n✅ Step 2 완료!")
    print(f"   컬렉션명: {collection_name}")
    print(f"   Qdrant URL: {QdrantConfig.URL}")

if __name__ == "__main__":
    create_collection()