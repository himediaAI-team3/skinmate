"""
질환 정보를 Vector DB에 인덱싱하는 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.vector_store import VectorStoreService
from app.core.config.qdrant import create_disease_qa_collection_if_not_exists
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """질환 정보 인덱싱 메인 함수"""
    try:
        # 1. 컬렉션 생성 (없을 경우)
        logger.info("질환 Q&A 컬렉션 생성 중...")
        create_disease_qa_collection_if_not_exists()
        
        # 2. Vector DB에 인덱싱 (내부에서 자동으로 파일 로드)
        logger.info("Vector DB 인덱싱 시작...")
        chunk_count = VectorStoreService.index_disease_info_batch(
            disease_files=None,  # None이면 자동으로 로드
            chunk_size=800,
            chunk_overlap=200
        )
        
        if chunk_count == 0:
            logger.error("인덱싱된 청크가 없습니다. 질환 정보 파일을 확인하세요.")
            return
        
        logger.info(f"인덱싱 완료: {chunk_count}개 청크 저장됨")
        
    except Exception as e:
        logger.error(f"인덱싱 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

