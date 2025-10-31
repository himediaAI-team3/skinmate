"""
Step 3: 제품 데이터 인덱싱
실행: python scripts/rag/3_index_products.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import mysql.connector
from dotenv import load_dotenv
import os
from qdrant_client.models import PointStruct
from tqdm import tqdm

from app.core.config.qdrant import qdrant_client, QdrantConfig
from app.core.config.embedding import embedding_model
from app.rag.vector_builder import create_embedding_text, create_sparse_vector

load_dotenv()

def index_products():
    print("=" * 60)
    print("Step 3: 제품 데이터 인덱싱")
    print("=" * 60)
    
    # Vocabulary 로드
    print("\n[1/5] Vocabulary 로드 중...")
    vocab_path = project_root / 'data' / 'vocabulary.json'
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocabulary = json.load(f)
    print(f"      → {len(vocabulary)}개 키워드 로드 완료")
    
    # MySQL 연결
    print("[2/5] MySQL 연결 중...")
    db_conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = db_conn.cursor(dictionary=True)
    
    # 데이터 로드
    print("[3/5] 화장품 데이터 로드 중...")
    cursor.execute("""
        SELECT 
            cosmetic_id, name, brand, category, price,
            skin_type, skin_disease, 
            main_effect, care_symptom, description, buy_url
        FROM cosmetic
    """)
    products = cursor.fetchall()
    print(f"      → {len(products)}개 제품 로드 완료")
    
    # 벡터 생성 및 삽입
    print("[4/5] 벡터 생성 및 Qdrant 삽입 중...")
    collection_name = QdrantConfig.COLLECTION_NAME
    points = []
    batch_size = 100
    
    for product in tqdm(products, desc="      인덱싱 진행"):
        # Dense vector
        embedding_text = create_embedding_text(product)
        dense_vector = embedding_model.encode(embedding_text).tolist()
        
        # Sparse vector
        sparse_vector = create_sparse_vector(product, vocabulary)
        
        # Payload
        payload = {
            "cosmetic_id": product['cosmetic_id'],
            "name": product['name'],
            "brand": product['brand'],
            "category": product['category'],
            "price": float(product['price']) if product['price'] else 0.0,
            "skin_type": product['skin_type'],
            "skin_disease": product['skin_disease'],
            "main_effect": product['main_effect'],
            "care_symptom": product['care_symptom'],
            "description": product['description'],
            "buy_url": product['buy_url']
        }
        
        # Point 생성
        point = PointStruct(
            id=product['cosmetic_id'],
            vector={
                "dense": dense_vector,
                "sparse": sparse_vector
            },
            payload=payload
        )
        
        points.append(point)
        
        # 배치 삽입
        if len(points) >= batch_size:
            qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            points = []
    
    # 남은 데이터 삽입
    if points:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    # 결과 확인
    print("[5/5] 인덱싱 결과 확인 중...")
    collection_info = qdrant_client.get_collection(collection_name)
    print(f"      → 총 {collection_info.points_count}개 제품 인덱싱 완료")
    
    # 정리
    cursor.close()
    db_conn.close()
    
    print("\n✅ Step 3 완료!")
    print(f"   인덱싱된 제품 수: {len(products)}")
    print(f"   컬렉션명: {collection_name}")

if __name__ == "__main__":
    index_products()