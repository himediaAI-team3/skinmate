"""데이터 확인 스크립트 (하이브리드 검색)"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config.database import SessionLocal
from app.models.cosmetic import Cosmetic
from app.services.vector_store import VectorStoreService

db = SessionLocal()

# MySQL 데이터 확인
print("=" * 80)
print("[MySQL 데이터 확인]")
print("=" * 80)

total = db.query(Cosmetic).count()
in_range = db.query(Cosmetic).filter(Cosmetic.price.between(1, 500000)).count()
acne_related = db.query(Cosmetic).filter(Cosmetic.skin_disease.like('%여드름%')).count()
oily_skin = db.query(Cosmetic).filter(Cosmetic.skin_type.like('%지성%')).count()

print(f"전체 화장품: {total}개")
print(f"가격범위 (1~500,000원): {in_range}개")
print(f"여드름 관련: {acne_related}개")
print(f"지성 피부용: {oily_skin}개")

# Qdrant 하이브리드 컬렉션 확인
print("\n" + "=" * 80)
print("[Qdrant 하이브리드 컬렉션 확인]")
print("=" * 80)

try:
    collection_info = VectorStoreService.get_collection_info()
    print(f"컬렉션명: {collection_info['name']}")
    print(f"Points 개수: {collection_info['points_count']}")
    print(f"Vectors 개수: {collection_info['vectors_count']}")
    print(f"Dense 차원: {collection_info['vector_dimension']}")
    print(f"상태: {collection_info['status']}")
except Exception as e:
    print(f"[ERROR] {e}")

# 하이브리드 검색 테스트 (필터 없이)
print("\n" + "=" * 80)
print("[하이브리드 검색 테스트 - 필터 없음]")
print("=" * 80)

dense_query = "여드름 피부입니다. 붉은 구진과 농포가 관찰됩니다."
sparse_query = "여드름 진정 클렌징"

results_no_filter = VectorStoreService.search_hybrid(
    query_dense_text=dense_query,
    query_sparse_text=sparse_query,
    limit=10
)
print(f"검색 결과: {len(results_no_filter)}개")

# 가격 필터만 적용
print("\n" + "=" * 80)
print("[하이브리드 검색 테스트 - 가격 필터만]")
print("=" * 80)

results_price_only = VectorStoreService.search_hybrid(
    query_dense_text=dense_query,
    query_sparse_text=sparse_query,
    min_price=1,
    max_price=500000,
    limit=10
)
print(f"검색 결과: {len(results_price_only)}개")
for i, r in enumerate(results_price_only[:5], 1):
    print(f"  {i}. {r['name']} - {r['price']}원 (유사도: {r['score']:.4f})")

# 모든 필터 적용
print("\n" + "=" * 80)
print("[하이브리드 검색 테스트 - 모든 필터]")
print("=" * 80)

results_all_filters = VectorStoreService.search_hybrid(
    query_dense_text=dense_query,
    query_sparse_text=sparse_query,
    disease_name="여드름",
    min_price=1,
    max_price=500000,
    skin_type="지성",
    limit=10
)
print(f"검색 결과: {len(results_all_filters)}개")
for i, r in enumerate(results_all_filters[:5], 1):
    print(f"  {i}. {r['name']} - {r['price']}원")
    print(f"     피부타입: {r['skin_type']}, 질환: {r['skin_disease']}")
    print(f"     유사도: {r['score']:.4f}")

db.close()

