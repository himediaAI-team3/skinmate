"""Qdrant 초기 데이터 적재 스크립트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.database import SessionLocal
from app.core.config.qdrant import create_collection_if_not_exists
from app.repository.cosmetic import CosmeticRepository
from app.services.vector_store import VectorStoreService


def main():
    print("\n[1/4] Collection 생성")
    create_collection_if_not_exists()
    
    print("[2/4] 화장품 데이터 조회")
    db = SessionLocal()
    
    try:
        cosmetics = CosmeticRepository.get_all(db)
        if not cosmetics:
            print("⚠️ 화장품 데이터가 없습니다.")
            return
        
        print(f"[3/4] Qdrant 업로드 ({len(cosmetics)}개)")
        VectorStoreService.upsert_cosmetics_from_models(cosmetics)
        
        print("[4/4] 검증")
        info = VectorStoreService.get_collection_info()
        print(f"✅ 완료: {info['points_count']}개 벡터\n")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

