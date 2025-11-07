"""
Vector Store 서비스: Qdrant 하이브리드 검색 (dense + BM25 sparse)
"""
from functools import lru_cache
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from qdrant_client.models import PointStruct, Filter, FieldCondition, Range, MatchAny, Prefetch
from fastembed import TextEmbedding, SparseTextEmbedding

from app.core.config.qdrant import get_qdrant_client, QDRANT_HYBRID_COLLECTION


def parse_comma_separated(value: str) -> list:
    """
    콤마로 구분된 문자열을 배열로 변환
    
    예: "민감성, 건성" -> ["민감성", "건성"]
    예: "여드름" -> ["여드름"]
    예: "" or None -> []
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_dense_model() -> TextEmbedding:
    """Dense 임베딩 모델 싱글톤 (LRU 캐시)"""
    return TextEmbedding("intfloat/multilingual-e5-large")


@lru_cache(maxsize=1)
def get_sparse_model() -> SparseTextEmbedding:
    """Sparse 임베딩 모델 싱글톤 (LRU 캐시)"""
    return SparseTextEmbedding("Qdrant/bm25")


class VectorStoreService:
    """Qdrant Vector Store 서비스 (하이브리드 검색)"""
    
    @staticmethod
    def create_dense_text(cosmetic) -> str:
        """Dense 임베딩용 텍스트: description 반환"""
        return cosmetic.description or ""
    
    @staticmethod
    def create_sparse_text(cosmetic) -> str:
        """Sparse(BM25) 임베딩용 텍스트: 질환명 + 피부타입 + 핵심성분 + 케어증상"""
        parts = []
        if cosmetic.skin_disease:
            parts.append(cosmetic.skin_disease)
        if cosmetic.skin_type:
            parts.append(cosmetic.skin_type)
        if cosmetic.key_ingredient:
            parts.append(cosmetic.key_ingredient)
        if cosmetic.care_symptom:
            parts.append(cosmetic.care_symptom)
        return " ".join(parts)
    
    @staticmethod
    def build_cosmetic_payload(cosmetic) -> Dict[str, Any]:
        """Payload 생성 (메타데이터)"""
        return {
            "cosmetic_id": cosmetic.cosmetic_id,
            "name": cosmetic.name or "",
            "brand": cosmetic.brand or "",
            "category": cosmetic.category or "",
            "price": int(cosmetic.price) if cosmetic.price else 0,
            "skin_types": parse_comma_separated(cosmetic.skin_type),
            "skin_diseases": parse_comma_separated(cosmetic.skin_disease),
        }
    
    @staticmethod
    def index_cosmetics_batch(
        db: Session, 
        cosmetic_ids: List[int] = None, 
        limit: int = None
    ) -> int:
        """배치 인덱싱: FastEmbed로 dense+sparse 임베딩 후 Qdrant 업서트"""
        from app.repository.cosmetic import CosmeticRepository
        
        # 1. DB 조회
        if cosmetic_ids:
            cosmetics = CosmeticRepository.get_by_ids(db, cosmetic_ids)
        else:
            cosmetics = CosmeticRepository.get_all(db)
            if limit:
                cosmetics = cosmetics[:limit]
        
        if not cosmetics:
            return 0
        
        # 2. 텍스트 준비
        dense_texts = [VectorStoreService.create_dense_text(c) for c in cosmetics]
        sparse_texts = [VectorStoreService.create_sparse_text(c) for c in cosmetics]
        
        # 3. FastEmbed 임베딩 (싱글톤 모델 사용)
        dense_model = get_dense_model()
        sparse_model = get_sparse_model()
        
        dense_vectors = list(dense_model.embed(dense_texts))
        sparse_vectors = list(sparse_model.embed(sparse_texts))
        
        # 4. Point 생성
        points = []
        for cosmetic, dense_vec, sparse_vec in zip(cosmetics, dense_vectors, sparse_vectors):
            point = PointStruct(
                id=cosmetic.cosmetic_id,
                vector={
                    "dense": dense_vec.tolist() if hasattr(dense_vec, 'tolist') else list(dense_vec),
                    "bm25": sparse_vec.as_object(),
                },
                payload=VectorStoreService.build_cosmetic_payload(cosmetic)
            )
            points.append(point)
        
        # 5. Qdrant 업서트
        client = get_qdrant_client()
        client.upsert(collection_name=QDRANT_HYBRID_COLLECTION, points=points)
        
        return len(points)
    
    @staticmethod
    def search_hybrid(
        query_dense_text: str,
        query_sparse_text: str,
        min_price: int = None,
        max_price: int = None,
        skin_type: str = None,
        disease_name: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """하이브리드 검색: Prefetch(dense+sparse) + 필터링"""
        client = get_qdrant_client()
        
        # 1. 쿼리 임베딩 (싱글톤 모델 사용)
        dense_model = get_dense_model()
        sparse_model = get_sparse_model()
        
        dense_query = list(dense_model.query_embed(query_dense_text))[0]
        sparse_query = list(sparse_model.query_embed(query_sparse_text))[0]
        
        # numpy array → list 변환
        dense_query_list = dense_query.tolist() if hasattr(dense_query, 'tolist') else list(dense_query)
        sparse_query_obj = sparse_query.as_object()
        
        # 2. Prefetch 구성
        prefetch = [
            Prefetch(query=dense_query_list, using="dense", limit=20),
            Prefetch(query=sparse_query_obj, using="bm25", limit=20),
        ]
        
        # 3. 필터 구성
        must_conditions = []
        should_conditions = []
        
        # 3-1. Price 하드 필터 (필수 조건)
        if min_price is not None and max_price is not None:
            must_conditions.append(
                FieldCondition(key="price", range=Range(gte=min_price, lte=max_price))
            )
        
        # 3-2. Skin Type 소프트 필터 (선호 조건)
        if skin_type:
            should_conditions.append(
                FieldCondition(
                    key="skin_types",
                    match=MatchAny(any=[skin_type])
                )
            )
        
        # 3-3. Disease 소프트 필터 (선호 조건)
        if disease_name:
            should_conditions.append(
                FieldCondition(
                    key="skin_diseases",
                    match=MatchAny(any=[disease_name])
                )
            )
        
        # 필터 조합
        query_filter = None
        if must_conditions or should_conditions:
            query_filter = Filter(
                must=must_conditions if must_conditions else None,
                should=should_conditions if should_conditions else None
            )
        
        # 4. 하이브리드 검색 (RRF 자동 병합)
        results = client.query_points(
            collection_name=QDRANT_HYBRID_COLLECTION,
            prefetch=prefetch,
            query=dense_query_list,
            using="dense",
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        
        # 5. 결과 변환
        output = []
        for r in results.points:
            output.append({
                "cosmetic_id": r.payload["cosmetic_id"],
                "score": r.score
            })
        
        return output
    
    @staticmethod
    def delete_cosmetic(cosmetic_id: int) -> bool:
        """화장품 데이터 삭제"""
        client = get_qdrant_client()
        client.delete(
            collection_name=QDRANT_HYBRID_COLLECTION,
            points_selector=[cosmetic_id]
        )
        return True
    
    @staticmethod
    def get_collection_info() -> Dict[str, Any]:
        """Collection 정보 조회"""
        client = get_qdrant_client()
        collection_info = client.get_collection(QDRANT_HYBRID_COLLECTION)
        
        return {
            "name": QDRANT_HYBRID_COLLECTION,
            "vector_dimension": collection_info.config.params.vectors.get("dense").size,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status
        }

