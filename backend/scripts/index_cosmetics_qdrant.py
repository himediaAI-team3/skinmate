"""
Qdrant 하이브리드 컬렉션 인덱싱 스크립트

사용법:
    # 전체 인덱싱
    python -m scripts.index_cosmetics_qdrant
    
    # 처음 10개만 인덱싱 (테스트용)
    python -m scripts.index_cosmetics_qdrant --limit 10
    
    # 특정 ID만 인덱싱
    python -m scripts.index_cosmetics_qdrant --ids 1,2,3,4,5
    
    # 컬렉션 재생성 후 전체 인덱싱
    python -m scripts.index_cosmetics_qdrant --rebuild
"""
import os
import sys
import argparse

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.database import SessionLocal
from app.services.vector_store import VectorStoreService
from app.core.config.qdrant import create_hybrid_collection_if_not_exists, get_qdrant_client, QDRANT_HYBRID_COLLECTION


def main():
    parser = argparse.ArgumentParser(description="Qdrant 하이브리드 컬렉션 인덱싱")
    parser.add_argument("--ids", type=str, help="cosmetic_id 목록 (콤마구분). 예) 12,34,56")
    parser.add_argument("--limit", type=int, help="앞에서부터 N개만 인덱싱")
    parser.add_argument("--rebuild", action="store_true", help="컬렉션 삭제 후 재생성")
    args = parser.parse_args()
    
    # 컬렉션 재생성
    if args.rebuild:
        print(f"[INFO] 기존 컬렉션 '{QDRANT_HYBRID_COLLECTION}' 삭제 중...")
        client = get_qdrant_client()
        try:
            client.delete_collection(QDRANT_HYBRID_COLLECTION)
            print(f"[INFO] 컬렉션 삭제 완료")
        except Exception as e:
            print(f"[WARN] 컬렉션 삭제 실패 (존재하지 않을 수 있음): {e}")
    
    # 컬렉션 생성/확인
    print(f"[INFO] 컬렉션 생성/확인 중...")
    create_hybrid_collection_if_not_exists()
    
    # 인덱싱
    db = SessionLocal()
    try:
        ids = None
        if args.ids:
            ids = [int(x.strip()) for x in args.ids.split(",") if x.strip()]
        
        print(f"[INFO] 인덱싱 시작...")
        count = VectorStoreService.index_cosmetics_batch(
            db, 
            cosmetic_ids=ids, 
            limit=args.limit
        )
        print(f"[SUCCESS] {count}개 인덱싱 완료")
        
        # 검증
        info = VectorStoreService.get_collection_info()
        print(f"[INFO] 컬렉션 상태: {info['points_count']}개 포인트")
        
    except Exception as e:
        print(f"[ERROR] 인덱싱 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

