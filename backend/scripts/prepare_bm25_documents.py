"""BM25 키워드 검색기를 위한 문서 피클 파일 생성.

이 스크립트는 다음 작업을 수행합니다:
    1) MySQL에서 화장품 제품 데이터 로드
    2) 각 행을 LangChain Document로 변환 (임베딩과 동일한 텍스트 형식)
    3) backend/scripts/bm25_documents.pkl 파일로 저장

사용법:
    python backend/scripts/prepare_bm25_documents.py
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import List

import mysql.connector
from dotenv import load_dotenv
from langchain_core.documents import Document


load_dotenv()


def create_embedding_text(product: dict) -> str:
    """구조화된 제품 데이터를 검색 최적화된 자연어 텍스트로 변환합니다.

    벡터 임베딩과 동일한 로직을 사용하여 BM25와 Dense 검색 간 일관성을 유지합니다.
    """
    parts = []
    parts.append(f"{product['brand']} {product['name']}")

    if product.get("key_ingredient"):
        parts.append(f"주요 성분은 {product['key_ingredient']}입니다.")

    if product.get("main_effect"):
        parts.append(f"{product['main_effect']} 효능이 있습니다.")

    if product.get("care_symptom"):
        parts.append(f"{product['care_symptom']} 증상을 완화하는 데 도움을 줍니다.")

    if product.get("skin_type"):
        parts.append(f"{product['skin_type']} 피부에 적합합니다.")

    if product.get("description"):
        parts.append(product["description"])

    return " ".join(parts)


def load_cosmetics_from_db() -> List[Document]:
    """MySQL에서 화장품 데이터를 로드하여 Document 리스트로 변환합니다."""
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306")),
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT 
            cosmetic_id, name, brand, category, price,
            skin_type, skin_disease, main_effect, care_symptom,
            key_ingredient, description
        FROM cosmetic
        """
    )
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    documents: List[Document] = []
    for product in products:
        page_content = create_embedding_text(product)
        metadata = {
            "cosmetic_id": product["cosmetic_id"],
            "name": product.get("name") or "",
            "price": float(product["price"]) if product["price"] else 0.0,
            "brand": product.get("brand") or "",
            "category": product.get("category") or "",
            "skin_type": product.get("skin_type") or "",
            "skin_disease": product.get("skin_disease") or "",
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents


def main() -> None:
    print("[1/3] MySQL에서 데이터 로드 중...")
    documents = load_cosmetics_from_db()
    print(f"      ✓ {len(documents)}개 제품 로드 완료")

    print("[2/3] Document 변환 중...")
    print("      ✓ 변환 완료")

    print("[3/3] backend/scripts/bm25_documents.pkl 저장 중...")
    out_path = Path(__file__).parent / "bm25_documents.pkl"
    with out_path.open("wb") as f:
        pickle.dump(documents, f)
    print("      ✓ 저장 완료")


if __name__ == "__main__":
    main()


