# scripts/rag/build_knowledge_base.py

"""
Qdrant 지식 DB 구축 (LangChain 표준)
실행: python scripts/rag/build_knowledge_base.py
"""

from langchain_core.documents import Document
try:
    from langchain_qdrant import QdrantVectorStore
except ImportError:
    try:
        from langchain_qdrant import Qdrant as QdrantVectorStore
    except ImportError:
        # langchain-community fallback
        from langchain_community.vectorstores import Qdrant as QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def create_embedding_text(product: dict) -> str:
    """구조화된 데이터를 검색 최적화된 자연어로 변환"""
    parts = []
    
    parts.append(f"{product['brand']} {product['name']}")
    
    if product.get('key_ingredient'):
        parts.append(f"주요 성분은 {product['key_ingredient']}입니다.")
    
    if product.get('main_effect'):
        parts.append(f"{product['main_effect']} 효능이 있습니다.")
    
    if product.get('care_symptom'):
        parts.append(f"{product['care_symptom']} 증상을 완화하는 데 도움을 줍니다.")
    
    if product.get('skin_type'):
        parts.append(f"{product['skin_type']} 피부에 적합합니다.")
    
    if product.get('description'):
        parts.append(product['description'])
    
    return " ".join(parts)


def load_cosmetics_from_db():
    """MySQL에서 화장품 데이터를 Document 리스트로 변환"""
    
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            cosmetic_id, name, brand, category, price,
            skin_type, main_effect, care_symptom, 
            key_ingredient, description
        FROM cosmetic
    """)
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    documents = []
    
    for product in products:
        page_content = create_embedding_text(product)
        
        metadata = {
            "cosmetic_id": product['cosmetic_id'],
            "price": float(product['price']) if product['price'] else 0.0,
            "brand": product['brand'] or "",
            "category": product['category'] or "",
        }
        
        documents.append(Document(
            page_content=page_content,
            metadata=metadata
        ))
    
    return documents


def build_qdrant_knowledge_base():
    """LangChain 표준 방식으로 Qdrant 지식 DB 구축"""
    
    print("=" * 60)
    print("Qdrant 지식 DB 구축")
    print("=" * 60)
    
    print("\n[1/4] MySQL에서 데이터 로드 중...")
    documents = load_cosmetics_from_db()
    print(f"      ✓ {len(documents)}개 제품 로드 완료")
    
    print("\n[2/4] 임베딩 모델 초기화 중...")
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv('EMBEDDING_MODEL', 'jhgan/ko-sroberta-multitask'),
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    print("      ✓ 임베딩 모델 로드 완료")
    
    print("\n[3/4] Qdrant 연결 및 기존 컬렉션 확인 중...")
    qdrant_client = QdrantClient(
        url=os.getenv('QDRANT_URL'),
        api_key=os.getenv('QDRANT_API_KEY')
    )
    
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'cosmetics')
    
    try:
        qdrant_client.delete_collection(collection_name)
        print(f"      ✓ 기존 '{collection_name}' 컬렉션 삭제")
    except Exception:
        print(f"      ✓ 기존 컬렉션 없음 (신규 생성)")
    
    print(f"\n[4/4] '{collection_name}' 컬렉션 생성 및 벡터 인덱싱 중...")
    print("      (임베딩 생성 중... 몇 분 소요될 수 있습니다)")
    
    vector_store = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=os.getenv('QDRANT_URL'),
        api_key=os.getenv('QDRANT_API_KEY'),
        collection_name=collection_name,
        force_recreate=True,
    )
    
    print(f"      ✓ {len(documents)}개 제품 인덱싱 완료")
    
    collection_info = qdrant_client.get_collection(collection_name)
    
    print("\n" + "=" * 60)
    print("✅ 구축 완료!")
    print("=" * 60)
    print(f"컬렉션명: {collection_name}")
    print(f"포인트 수: {collection_info.points_count}")
    print(f"벡터 차원: 768")
    print(f"거리 측정: COSINE")
    print(f"URL: {os.getenv('QDRANT_URL')}")


if __name__ == "__main__":
    build_qdrant_knowledge_base()