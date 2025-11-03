"""
BM25용 IDF 사전 계산
실행: python scripts/rag/5_calculate_bm25_idf.py
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import math
from collections import defaultdict
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def calculate_bm25_idf():
    print("=" * 60)
    print("BM25 IDF 계산")
    print("=" * 60)
    
    # 1) Vocabulary 로드
    vocab_path = project_root / 'data' / 'vocabulary.json'
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocabulary = json.load(f)
    print(f"Vocabulary: {len(vocabulary)}개 키워드")
    
    # 2) MySQL 연결
    db_conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = db_conn.cursor(dictionary=True)
    
    # 3) 전체 제품 로드
    cursor.execute("SELECT cosmetic_id, main_effect, care_symptom FROM cosmetic")
    products = cursor.fetchall()
    N = len(products)
    print(f"전체 제품 수: {N}개")
    
    # 4) 각 키워드가 몇 개 문서에 등장하는지 계산 (Document Frequency)
    df = defaultdict(int)  # document frequency
    
    for product in products:
        # 이 제품에 등장하는 고유 키워드 수집
        product_keywords = set()
        
        if product['main_effect']:
            keywords = [k.strip() for k in product['main_effect'].split(',')]
            product_keywords.update(keywords)
        
        if product['care_symptom']:
            keywords = [k.strip() for k in product['care_symptom'].split(',')]
            product_keywords.update(keywords)
        
        # 각 키워드에 대해 df 증가
        for keyword in product_keywords:
            if keyword in vocabulary:
                df[keyword] += 1
    
    # 5) IDF 계산
    # IDF = log((N - df + 0.5) / (df + 0.5) + 1)
    idf = {}
    for keyword in vocabulary.keys():
        doc_freq = df.get(keyword, 0)
        if doc_freq == 0:
            # 한 번도 안 나온 키워드는 최대 IDF
            idf[keyword] = math.log(N + 1)
        else:
            # BM25 IDF 공식
            idf[keyword] = math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
    
    # 6) 통계 출력
    print(f"\nIDF 통계:")
    sorted_idf = sorted(idf.items(), key=lambda x: x[1], reverse=True)
    print(f"  최고 IDF (희귀): {sorted_idf[:5]}")
    print(f"  최저 IDF (흔함): {sorted_idf[-5:]}")
    
    # 7) 저장
    idf_path = project_root / 'data' / 'bm25_idf.json'
    with open(idf_path, 'w', encoding='utf-8') as f:
        json.dump(idf, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ IDF 저장 완료: {idf_path}")
    
    cursor.close()
    db_conn.close()

if __name__ == "__main__":
    calculate_bm25_idf()