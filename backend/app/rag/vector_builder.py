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


    def create_bm25_sparse_vector(
    product: Dict, 
    vocabulary: Dict[str, int], 
    idf: Dict[str, float],
    k1: float = 1.2,
    b: float = 0.75,
    avgdl: float = 5.0  # 평균 키워드 개수 (조정 가능)
) -> SparseVector:
        """
        BM25 기반 Sparse Vector 생성
        
        Args:
            product: 화장품 데이터
            vocabulary: 키워드 인덱스 매핑
            idf: IDF 사전
            k1: TF 포화 파라미터 (1.2~2.0)
            b: 길이 정규화 (0~1, 보통 0.75)
            avgdl: 평균 문서 길이 (키워드 개수)
        
        Returns:
            SparseVector 객체
        """
    from collections import Counter
    
    keywords = []
    
    # main_effect 키워드
    if product.get('main_effect'):
        keywords += [k.strip() for k in product['main_effect'].split(',')]
    
    # care_symptom 키워드
    if product.get('care_symptom'):
        keywords += [k.strip() for k in product['care_symptom'].split(',')]
    
    # 빈도수 계산
    keyword_counts = Counter(keywords)
    
    # 문서 길이
    doc_length = len(keywords)
    
    # BM25 점수 계산
    indices = []
    values = []
    
    for keyword, tf in keyword_counts.items():
        if keyword not in vocabulary:
            continue
        
        # IDF
        keyword_idf = idf.get(keyword, 0.0)
        
        # BM25 score
        # score = IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avgdl)))
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_length / avgdl))
        bm25_score = keyword_idf * (numerator / denominator)
        
        indices.append(vocabulary[keyword])
        values.append(float(bm25_score))
    
    return SparseVector(indices=indices, values=values)


def create_search_bm25_sparse_vector(
    keywords: List[str], 
    vocabulary: Dict[str, int],
    idf: Dict[str, float]
) -> SparseVector:
    """
    검색용 BM25 Sparse Vector 생성
    
    Args:
        keywords: 검색 키워드 리스트
        vocabulary: 키워드 인덱스 매핑
        idf: IDF 사전
    
    Returns:
        SparseVector 객체
    """
    indices = []
    values = []
    
    for keyword in keywords:
        keyword = keyword.strip()
        if keyword in vocabulary:
            # 검색 쿼리는 TF=1로 가정, IDF만 사용
            keyword_idf = idf.get(keyword, 0.0)
            indices.append(vocabulary[keyword])
            values.append(keyword_idf)
    
    return SparseVector(indices=indices, values=values)