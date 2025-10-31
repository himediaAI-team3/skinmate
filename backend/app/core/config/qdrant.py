"""Qdrant 연결 설정"""
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

class QdrantConfig:
    """Qdrant 설정 클래스"""
    
    URL = os.getenv('QDRANT_URL')
    API_KEY = os.getenv('QDRANT_API_KEY')
    COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'cosmetics')
    
    @staticmethod
    def get_client() -> QdrantClient:
        """Qdrant 클라이언트 반환"""
        return QdrantClient(
            url=QdrantConfig.URL,
            api_key=QdrantConfig.API_KEY
        )

# 싱글톤 인스턴스
qdrant_client = QdrantConfig.get_client()