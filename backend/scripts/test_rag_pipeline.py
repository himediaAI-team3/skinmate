from __future__ import annotations

"""E2E test for full RAG pipeline (Step 3)."""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.rag import recommend_products
from app.core.config.database import SessionLocal


def test_full_pipeline() -> None:
    db = SessionLocal()
    try:
        analysis_id = 1  # Change to an existing analysis_id

        print("=" * 60)
        print(f"RAG 파이프라인 테스트 (analysis_id={analysis_id})")
        print("=" * 60)

        # 1) Run pipeline
        print("\n[1] 파이프라인 실행 중...")
        recommendations = recommend_products(db, analysis_id)
        print(f"   ✓ {len(recommendations)}개 추천 생성 완료")

        # 2) Print results
        print("\n[2] 추천 결과:")
        for rec in recommendations:
            print(f"\n{rec['ranking']}위")
            print(f"  제품 ID: {rec['cosmetic_id']}")
            print(f"  추천 이유: {rec['reason']}")

        print("\n✅ 테스트 완료")
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_full_pipeline()


