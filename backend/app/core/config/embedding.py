"""임베딩 모델 설정"""
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class EmbeddingConfig:
    """임베딩 모델 설정 클래스"""
    
    MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'jhgan/ko-sroberta-multitask')
    VECTOR_SIZE = 768  # ko-sroberta 차원
    
    _model = None
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """임베딩 모델 반환 (싱글톤)"""
        if cls._model is None:
            print(f"🔄 임베딩 모델 로딩: {cls.MODEL_NAME}")
            cls._model = SentenceTransformer(cls.MODEL_NAME)
            print("✅ 임베딩 모델 로딩 완료")
        return cls._model

# 싱글톤 인스턴스
embedding_model = EmbeddingConfig.get_model()