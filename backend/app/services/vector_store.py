"""
Vector Store 서비스: Qdrant CRUD 작업
"""
from typing import List, Optional, Dict, Any
from qdrant_client.models import PointStruct, Filter, FieldCondition, Range, MatchValue
from app.core.config.qdrant import get_qdrant_client, QDRANT_COLLECTION_NAME
from app.services.embedding import EmbeddingService


class VectorStoreService:
    """Qdrant Vector Store 서비스"""
    
    @staticmethod
    def create_embedding_text(cosmetic) -> str:
        """화장품 정보를 임베딩용 자연어 텍스트로 변환"""
        parts = []
        
        if cosmetic.description:
            parts.append(cosmetic.description)
        if cosmetic.short_description:
            parts.append(f"이 화장품의 주요 특징은 {cosmetic.short_description}입니다.")
        if cosmetic.main_effect:
            parts.append(f"주요 효능은 {cosmetic.main_effect}입니다.")
        if cosmetic.care_symptom:
            parts.append(f"{cosmetic.care_symptom} 증상을 케어합니다.")
        if cosmetic.key_ingredient:
            parts.append(f"핵심 성분은 {cosmetic.key_ingredient}입니다.")
        
        return " ".join(parts)
    
    @staticmethod
    def create_metadata(cosmetic) -> Dict[str, Any]:
        """화장품 메타데이터 구성"""
        return {
            "cosmetic_id": cosmetic.cosmetic_id,
            "name": cosmetic.name,
            "brand": cosmetic.brand,
            "category": cosmetic.category,
            "price": int(cosmetic.price) if cosmetic.price else 0,
            "skin_type": cosmetic.skin_type or "",
            "skin_disease": cosmetic.skin_disease or "",
        }
    
    @staticmethod
    def upsert_cosmetic_from_model(cosmetic) -> bool:
        """Cosmetic 모델을 받아서 Qdrant에 자동 적재 (고수준 함수)"""
        embedded_text = VectorStoreService.create_embedding_text(cosmetic)
        metadata = VectorStoreService.create_metadata(cosmetic)
        
        return VectorStoreService.upsert_cosmetic(
            cosmetic_id=cosmetic.cosmetic_id,
            embedded_text=embedded_text,
            metadata=metadata
        )
    
    @staticmethod
    def upsert_cosmetics_from_models(cosmetics: List) -> bool:
        """여러 Cosmetic 모델을 배치로 Qdrant에 적재 (고수준 함수)"""
        cosmetics_data = []
        for cosmetic in cosmetics:
            embedded_text = VectorStoreService.create_embedding_text(cosmetic)
            metadata = VectorStoreService.create_metadata(cosmetic)
            cosmetics_data.append({
                "cosmetic_id": cosmetic.cosmetic_id,
                "embedded_text": embedded_text,
                "metadata": metadata
            })
        
        return VectorStoreService.upsert_cosmetics_batch(cosmetics_data)
    
    @staticmethod
    def upsert_cosmetic(
        cosmetic_id: int,
        embedded_text: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """단일 화장품 데이터를 Qdrant에 적재 (저수준 함수)"""
        client = get_qdrant_client()
        
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[PointStruct(
                id=cosmetic_id,
                vector=EmbeddingService.embed_text(embedded_text),
                payload=metadata
            )]
        )
        return True
    
    @staticmethod
    def upsert_cosmetics_batch(
        cosmetics_data: List[Dict[str, Any]]
    ) -> bool:
        """여러 화장품 데이터를 배치로 Qdrant에 적재 (저수준 함수)"""
        client = get_qdrant_client()
        
        texts = [item["embedded_text"] for item in cosmetics_data]
        vectors = EmbeddingService.embed_texts(texts, show_progress=True)
        
        points = [
            PointStruct(
                id=item["cosmetic_id"],
                vector=vector,
                payload=item["metadata"]
            )
            for item, vector in zip(cosmetics_data, vectors)
        ]
        
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        
        return True
    
    @staticmethod
    def search_similar(
        query_text: str,
        disease_name: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        skin_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """유사 화장품 검색 (가격 필터 + 질환/피부타입 가점)"""
        client = get_qdrant_client()
        query_vector = EmbeddingService.embed_query(query_text)
        
        must_conditions = []
        
        if min_price is not None and max_price is not None:
            must_conditions.append(
                FieldCondition(
                    key="price",
                    range=Range(gte=min_price, lte=max_price)
                )
            )
        
        search_filter = Filter(must=must_conditions) if must_conditions else None
        
        search_results = client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=30,
            with_payload=True
        )
        
        # 질환/피부타입 매칭 시 가점 부여
        for result in search_results:
            bonus = 0.0
            if disease_name and disease_name in result.payload.get("skin_disease", ""):
                bonus += 0.01
            if skin_type and skin_type in result.payload.get("skin_type", ""):
                bonus += 0.005
            result.score += bonus
        
        search_results.sort(key=lambda x: x.score, reverse=True)
        search_results = search_results[:limit]
        
        results = []
        for result in search_results:
            results.append({
                "cosmetic_id": result.payload.get("cosmetic_id"),
                "score": result.score,
                "name": result.payload.get("name"),
                "brand": result.payload.get("brand"),
                "category": result.payload.get("category"),
                "price": result.payload.get("price"),
                "skin_type": result.payload.get("skin_type"),
                "skin_disease": result.payload.get("skin_disease"),
            })
        
        return results
    
    @staticmethod
    def delete_cosmetic(cosmetic_id: int) -> bool:
        """화장품 데이터 삭제"""
        client = get_qdrant_client()
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=[cosmetic_id]
        )
        return True
    
    @staticmethod
    def get_collection_info() -> Dict[str, Any]:
        """Collection 정보 조회"""
        client = get_qdrant_client()
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        
        return {
            "name": QDRANT_COLLECTION_NAME,
            "vector_dimension": collection_info.config.params.vectors.size,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status
        }

