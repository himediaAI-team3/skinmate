"""
Step 1: Vocabulary 구축
실행: python scripts/rag/1_build_vocabulary.py
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def build_vocabulary():
    print("=" * 60)
    print("Step 1: Vocabulary 구축 시작")
    print("=" * 60)
    
    # MySQL 연결
    print("\n[1/4] MySQL 연결 중...")
    db_conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = db_conn.cursor(dictionary=True)
    
    # 데이터 로드
    print("[2/4] 화장품 데이터 로드 중...")
    cursor.execute("""
        SELECT main_effect, care_symptom 
        FROM cosmetic 
        WHERE main_effect IS NOT NULL OR care_symptom IS NOT NULL
    """)
    products = cursor.fetchall()
    print(f"      → {len(products)}개 제품 로드 완료")
    
    # 키워드 수집
    print("[3/4] 키워드 추출 중...")
    all_keywords = set()
    
    for product in products:
        # main_effect 키워드
        if product['main_effect']:
            keywords = [k.strip() for k in product['main_effect'].split(',')]
            all_keywords.update(keywords)
        
        # care_symptom 키워드
        if product['care_symptom']:
            keywords = [k.strip() for k in product['care_symptom'].split(',')]
            all_keywords.update(keywords)
    
    # Vocabulary 생성 (정렬)
    vocabulary = {keyword: idx for idx, keyword in enumerate(sorted(all_keywords))}
    
    print(f"      → {len(vocabulary)}개 고유 키워드 추출")
    print(f"      → 예시 키워드: {list(vocabulary.keys())[:10]}")
    
    # 저장
    print("[4/4] vocabulary.json 저장 중...")
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    
    vocab_path = data_dir / 'vocabulary.json'
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)
    
    print(f"      → {vocab_path} 저장 완료")
    
    # 정리
    cursor.close()
    db_conn.close()
    
    print("\n✅ Step 1 완료!")
    print(f"   Vocabulary 크기: {len(vocabulary)}")
    print(f"   저장 위치: {vocab_path}")
    
    return vocabulary

if __name__ == "__main__":
    build_vocabulary()