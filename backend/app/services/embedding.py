"""
임베딩 서비스: 텍스트를 벡터로 변환
multilingual-e5-large 모델 사용
"""
import os
from typing import List
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# 임베딩 모델 설정
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")

# 모델 캐싱 (한 번만 로드)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    임베딩 모델 로드 (Singleton 패턴)
    
    Returns:
        SentenceTransformer: 임베딩 모델 인스턴스
    """
    global _model
    
    if _model is None:
        print(f"[임베딩 모델 로딩 중] {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[임베딩 모델 로딩 완료] 벡터 차원: {_model.get_sentence_embedding_dimension()}")
    
    return _model


class EmbeddingService:
    """임베딩 서비스 클래스"""
    
    @staticmethod
    def embed_text(text: str) -> List[float]:
        """
        단일 텍스트 임베딩
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            List[float]: 1024-dim 벡터
        """
        model = get_embedding_model()
        
        # multilingual-e5 모델은 쿼리에 prefix 추가 권장
        # 하지만 화장품 설명은 passage이므로 prefix 없이 사용
        vector = model.encode(text, convert_to_numpy=True)
        
        return vector.tolist()
    
    @staticmethod
    def embed_texts(texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        배치 텍스트 임베딩 (효율적)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            show_progress: 진행률 표시 여부
            
        Returns:
            List[List[float]]: 벡터 리스트
        """
        model = get_embedding_model()
        
        vectors = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress,
            batch_size=32  # 배치 크기
        )
        
        return [vec.tolist() for vec in vectors]
    
    @staticmethod
    def embed_query(query_text: str) -> List[float]:
        """
        검색 쿼리 임베딩 (prefix 추가)
        
        Args:
            query_text: 검색 쿼리 텍스트
            
        Returns:
            List[float]: 1024-dim 벡터
        """
        model = get_embedding_model()
        
        # 검색 쿼리는 "query: " prefix 추가 (multilingual-e5 권장)
        prefixed_query = f"query: {query_text}"
        vector = model.encode(prefixed_query, convert_to_numpy=True)
        
        return vector.tolist()

