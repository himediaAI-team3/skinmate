"""벡터 생성 유틸리티"""
from collections import Counter
from typing import Dict, List
from qdrant_client.models import SparseVector

def create_embedding_text(product: Dict) -> str:
    """
    Dense Vector용 임베딩 텍스트 생성
    
    Args:
        product: 화장품 데이터 (dict)
    
    Returns:
        구조화된 텍스트
    """
    text = f"""
{product['name']}는 {product['brand']}의 {product['category']} 제품입니다.
주요 효능: {product['main_effect']}
케어 증상: {product['care_symptom']}
피부 타입: {product['skin_type']}

{product['description']}
""".strip()
    
    return text


def create_sparse_vector(product: Dict, vocabulary: Dict[str, int]) -> SparseVector:
    """
    Sparse Vector 생성 (main_effect + care_symptom)
    
    Args:
        product: 화장품 데이터
        vocabulary: 키워드 인덱스 매핑
    
    Returns:
        SparseVector 객체
    """
    keywords = []
    
    # main_effect 키워드
    if product.get('main_effect'):
        keywords += [k.strip() for k in product['main_effect'].split(',')]
    
    # care_symptom 키워드
    if product.get('care_symptom'):
        keywords += [k.strip() for k in product['care_symptom'].split(',')]
    
    # 빈도수 계산
    keyword_counts = Counter(keywords)
    
    # Sparse vector 생성
    indices = []
    values = []
    
    for keyword, count in keyword_counts.items():
        if keyword in vocabulary:
            indices.append(vocabulary[keyword])
            values.append(float(count))
    
    return SparseVector(indices=indices, values=values)


def create_search_sparse_vector(keywords: List[str], vocabulary: Dict[str, int]) -> SparseVector:
    """
    검색용 Sparse Vector 생성
    
    Args:
        keywords: 검색 키워드 리스트
        vocabulary: 키워드 인덱스 매핑
    
    Returns:
        SparseVector 객체
    """
    indices = []
    values = []
    
    for keyword in keywords:
        keyword = keyword.strip()
        if keyword in vocabulary:
            indices.append(vocabulary[keyword])
            values.append(1.0)
    
    return SparseVector(indices=indices, values=values)