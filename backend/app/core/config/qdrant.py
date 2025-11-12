"""
Qdrant Cloud 설정 및 클라이언트 초기화
"""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType, SparseVectorParams, Modifier
from dotenv import load_dotenv

load_dotenv()

# Qdrant 설정
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "skinmate_cosmetics")
QDRANT_HYBRID_COLLECTION = "skinmate_cosmetics_hybrid"  # 하이브리드 컬렉션명
QDRANT_DISEASE_QA_COLLECTION = "skinmate_disease_qa"  # 질환 Q&A 컬렉션명

# 벡터 차원 (multilingual-e5-large)
VECTOR_DIMENSION = 1024

# Qdrant Client 싱글톤
_client = None


def get_qdrant_client() -> QdrantClient:
    """
    Qdrant Cloud 클라이언트 생성 (싱글톤 패턴)
    
    Returns:
        QdrantClient: Qdrant 클라이언트 인스턴스
    """
    global _client
    
    if _client is None:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise ValueError(
                "Qdrant 설정이 누락되었습니다. "
                ".env 파일에 QDRANT_URL, QDRANT_API_KEY를 설정하세요."
            )
        
        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
    
    return _client


def create_collection_if_not_exists():
    """
    Qdrant Collection 생성 (없을 경우에만)
    """
    client = get_qdrant_client()
    
    # Collection 존재 여부 확인
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if QDRANT_COLLECTION_NAME not in collection_names:
        # Collection 생성
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIMENSION,
                distance=Distance.COSINE  # 코사인 유사도
            )
        )
        print(f"Collection '{QDRANT_COLLECTION_NAME}' 생성 완료")
        
        # 필터링에 필요한 필드 인덱스 생성
        print("Payload 인덱스 생성 중...")
        
        # price 필드 인덱스 (integer)
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION_NAME,
            field_name="price",
            field_schema=PayloadSchemaType.INTEGER
        )
        
        # skin_disease 필드 인덱스 (keyword)
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION_NAME,
            field_name="skin_disease",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        # skin_type 필드 인덱스 (keyword)
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION_NAME,
            field_name="skin_type",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        print("Payload 인덱스 생성 완료")
    else:
        print(f"Collection '{QDRANT_COLLECTION_NAME}' 이미 존재")


def create_hybrid_collection_if_not_exists():
    """
    하이브리드 컬렉션 생성 (dense + BM25 sparse)
    """
    client = get_qdrant_client()
    
    # Collection 존재 여부 확인
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if QDRANT_HYBRID_COLLECTION not in collection_names:
        # 컬렉션 생성 (dense + sparse 벡터)
        client.create_collection(
            collection_name=QDRANT_HYBRID_COLLECTION,
            vectors_config={
                "dense": VectorParams(
                    size=VECTOR_DIMENSION,
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "bm25": SparseVectorParams(
                    modifier=Modifier.IDF
                )
            }
        )
        print(f"하이브리드 컬렉션 '{QDRANT_HYBRID_COLLECTION}' 생성 완료")
        
        # Payload 인덱스 생성
        print("Payload 인덱스 생성 중...")
        client.create_payload_index(
            collection_name=QDRANT_HYBRID_COLLECTION,
            field_name="price",
            field_schema=PayloadSchemaType.INTEGER
        )
        client.create_payload_index(
            collection_name=QDRANT_HYBRID_COLLECTION,
            field_name="skin_diseases",
            field_schema=PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=QDRANT_HYBRID_COLLECTION,
            field_name="skin_types",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Payload 인덱스 생성 완료")
    else:
        print(f"하이브리드 컬렉션 '{QDRANT_HYBRID_COLLECTION}' 이미 존재")


def create_disease_qa_collection_if_not_exists():
    """
    질환 Q&A 컬렉션 생성 (dense + BM25 sparse)
    """
    client = get_qdrant_client()
    
    # Collection 존재 여부 확인
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if QDRANT_DISEASE_QA_COLLECTION not in collection_names:
        # 컬렉션 생성 (dense + sparse 벡터)
        client.create_collection(
            collection_name=QDRANT_DISEASE_QA_COLLECTION,
            vectors_config={
                "dense": VectorParams(
                    size=VECTOR_DIMENSION,
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "bm25": SparseVectorParams(
                    modifier=Modifier.IDF
                )
            }
        )
        print(f"질환 Q&A 컬렉션 '{QDRANT_DISEASE_QA_COLLECTION}' 생성 완료")
        
        # Payload 인덱스 생성
        print("Payload 인덱스 생성 중...")
        client.create_payload_index(
            collection_name=QDRANT_DISEASE_QA_COLLECTION,
            field_name="disease_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=QDRANT_DISEASE_QA_COLLECTION,
            field_name="file_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Payload 인덱스 생성 완료")
    else:
        print(f"질환 Q&A 컬렉션 '{QDRANT_DISEASE_QA_COLLECTION}' 이미 존재")

