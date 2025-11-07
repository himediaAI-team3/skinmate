import os
import sys
import argparse
from typing import List, Optional

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.database import SessionLocal
from app.repository.cosmetic import CosmeticRepository
from app.services.cosmetic_enrichment import CosmeticEnrichmentService


def parse_id_list(ids_str: str) -> List[int]:
    return [int(x.strip()) for x in ids_str.split(',') if x.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="LLM로 cosmetic 6개 확장 컬럼 생성 및 저장 스크립트"
    )
    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help="샘플용: 갱신할 cosmetic_id 목록(콤마구분). 예) 12,34,56"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="샘플용: 전체 중 앞에서부터 N개만 처리"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="생성 결과만 출력하고 DB 저장은 하지 않음"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="항상 새 값으로 덮어쓰기(기본값: True)"
    )
    parser.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="덮어쓰지 않음(현재 리포지토리 로직은 항상 덮어쓰기 수행)"
    )
    parser.set_defaults(overwrite=True)

    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY 환경변수를 설정하세요.")

    db = SessionLocal()
    processed = 0
    success = 0
    failed = 0

    try:
        targets: List[int]
        if args.ids:
            targets = parse_id_list(args.ids)
        else:
            rows = CosmeticRepository.get_all(db)
            if args.limit is not None:
                rows = rows[: args.limit]
            targets = [r.cosmetic_id for r in rows]

        if not targets:
            print("[INFO] 처리할 대상이 없습니다.")
            return

        print(f"[INFO] 대상 개수: {len(targets)} (dry-run={args.dry_run})")

        for cid in targets:
            processed += 1
            try:
                if args.dry_run:
                    data = CosmeticEnrichmentService.generate_cosmetic_llm_fields(db, cid)
                    print(f"\n[DRY-RUN] cosmetic_id={cid}")
                    for k, v in data.items():
                        print(f"  - {k}: {v}")
                    success += 1
                else:
                    CosmeticEnrichmentService.enrich_cosmetic_and_save(
                        db,
                        cosmetic_id=cid,
                        overwrite=args.overwrite,
                        upsert=True,
                    )
                    print(f"[OK] cosmetic_id={cid}")
                    success += 1
            except Exception as e:
                print(f"[FAIL] cosmetic_id={cid} - {e}")
                failed += 1

        print("\n=== 결과 요약 ===")
        print(f"처리 시도: {processed}")
        print(f"성공: {success}")
        print(f"실패: {failed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()


