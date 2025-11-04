"""
Vector Store 서비스: Qdrant 하이브리드 검색 (dense + BM25 sparse)
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from qdrant_client.models import PointStruct, Filter, FieldCondition, Range, MatchValue, Prefetch
from app.core.config.qdrant import get_qdrant_client, QDRANT_HYBRID_COLLECTION
from fastembed import TextEmbedding, SparseTextEmbedding


class VectorStoreService:
    """Qdrant Vector Store 서비스 (하이브리드 검색)"""
    
    @staticmethod
    def create_dense_text(cosmetic) -> str:
        """Dense 임베딩용 텍스트: description 반환"""
        return cosmetic.description or ""
    
    @staticmethod
    def create_sparse_text(cosmetic) -> str:
        """Sparse(BM25) 임베딩용 텍스트: brand + 핵심성분 + 케어증상"""
        parts = []
        if cosmetic.brand:
            parts.append(cosmetic.brand)
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
            "skin_type": cosmetic.skin_type or "",
            "skin_disease": cosmetic.skin_disease or "",
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
        
        # 3. FastEmbed 임베딩
        dense_model = TextEmbedding("intfloat/multilingual-e5-large")
        sparse_model = SparseTextEmbedding("Qdrant/bm25")
        
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
        
        # 1. 쿼리 임베딩
        dense_model = TextEmbedding("intfloat/multilingual-e5-large")
        sparse_model = SparseTextEmbedding("Qdrant/bm25")
        
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
        
        if min_price is not None and max_price is not None:
            must_conditions.append(
                FieldCondition(key="price", range=Range(gte=min_price, lte=max_price))
            )
        
        if disease_name:
            should_conditions.append(
                FieldCondition(key="skin_disease", match=MatchValue(value=disease_name))
            )
        
        if skin_type:
            should_conditions.append(
                FieldCondition(key="skin_type", match=MatchValue(value=skin_type))
            )
        
        query_filter = None
        if must_conditions or should_conditions:
            query_filter = Filter(must=must_conditions, should=should_conditions)
        
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
                "score": r.score,
                "name": r.payload["name"],
                "brand": r.payload["brand"],
                "category": r.payload["category"],
                "price": r.payload["price"],
                "skin_type": r.payload["skin_type"],
                "skin_disease": r.payload["skin_disease"],
            })
        
        return output
    
    @staticmethod
    def _build_search_query_from_diagnosis(db: Session, analysis_id: int) -> dict:
        """진단 결과를 검색 쿼리로 변환 (LLM 호출)"""
        from app.repository.diagnosis import DiagnosisRepository
        from app.utils.prompt import load_prompt
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        import json
        import os
        import logging
        
        logger = logging.getLogger(__name__)
        
        diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
        if not diagnosis:
            raise ValueError(f"진단 결과를 찾을 수 없습니다: analysis_id={analysis_id}")
        
        instruction = load_prompt("summary_refine.yaml")
        filled = instruction.format(
            disease_name=diagnosis.disease_name,
            summary=diagnosis.summary
        )
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
        )
        
        resp = llm.invoke([HumanMessage(content=filled)])
        
        # JSON 파싱 (코드블록 제거)
        content = resp.content.strip()
        if content.startswith("```"):
            content = content.strip("`").strip("json").strip()
        
        data = json.loads(content)
        
        logger.info(f"검색 쿼리 생성 완료: dense={data['dense_query'][:50]}...")
        try:
            logger.info(f"검색 쿼리 생성 완료: sparse={data['sparse_keywords'][:80]}...")
        except Exception:
            pass
        
        return {
            "disease_name": data["disease_name"],
            "dense_query": data["dense_query"],
            "sparse_keywords": data["sparse_keywords"],
        }
    
    @staticmethod
    def search_by_analysis(
        db: Session, 
        analysis_id: int, 
        member_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """진단 결과 기반 검색: 진단→쿼리 생성→하이브리드 검색"""
        from app.repository.member import MemberRepository
        
        # 1. 쿼리 생성
        query_data = VectorStoreService._build_search_query_from_diagnosis(db, analysis_id)
        
        # 2. 회원 정보 조회
        member = MemberRepository.get_by_id(db, member_id)
        
        # 3. 하이브리드 검색
        return VectorStoreService.search_hybrid(
            query_dense_text=query_data["dense_query"],
            query_sparse_text=query_data["sparse_keywords"],
            min_price=member.min_price if member else None,
            max_price=member.max_price if member else None,
            skin_type=member.skin_type if member else None,
            disease_name=query_data.get("disease_name"),
            limit=limit
        )
    
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

