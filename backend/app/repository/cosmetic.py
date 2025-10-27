from sqlalchemy.orm import Session
from sqlalchemy import func, select, literal
from typing import List, Tuple, Optional
from app.models.cosmetic import Cosmetic
from app.models.like import Like
from app.models.file import File
from app.models.entity_type import EntityType


class CosmeticRepository:
    
    @staticmethod
    def exists(db: Session, cosmetic_id: int) -> bool:
        """화장품 존재 여부 확인"""
        return db.query(Cosmetic).filter(Cosmetic.cosmetic_id == cosmetic_id).count() > 0
    
    @staticmethod
    def search(
        db: Session, 
        brand: Optional[str] = None,
        name: Optional[str] = None,
        skin_type: Optional[str] = None,
        category: Optional[str] = None,
        member_id: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[dict], int]:
        """화장품 목록 검색 (페이징 포함)"""
        
        # 서브쿼리: 좋아요 개수
        like_count_sq = select(func.count(Like.like_id)).where(
            Like.cosmetic_id == Cosmetic.cosmetic_id
        ).scalar_subquery()
        
        # 서브쿼리: 대표 이미지 file_path
        file_path_sq = select(File.file_path).where(
            File.entity_type == EntityType.COSMETIC,
            File.entity_id == Cosmetic.cosmetic_id
        ).order_by(File.file_id.asc()).limit(1).scalar_subquery()
        
        # 서브쿼리: 사용자 좋아요 여부
        if member_id:
            is_liked_sq = select(func.count(Like.like_id) > 0).where(
                Like.cosmetic_id == Cosmetic.cosmetic_id,
                Like.member_id == member_id
            ).scalar_subquery()
        else:
            is_liked_sq = literal(False)
        
        # 메인 쿼리
        query = db.query(
            Cosmetic.cosmetic_id,
            Cosmetic.name,
            Cosmetic.brand,
            Cosmetic.category,
            Cosmetic.price,
            file_path_sq.label('file_path'),
            like_count_sq.label('like_count'),
            is_liked_sq.label('is_liked')
        )
        
        # 필터 적용
        if brand:
            query = query.filter(Cosmetic.brand.ilike(f"%{brand}%"))
        if name:
            query = query.filter(Cosmetic.name.ilike(f"%{name}%"))
        if skin_type:
            query = query.filter(Cosmetic.skin_type.ilike(f"%{skin_type}%"))
        if category:
            query = query.filter(Cosmetic.category == category)
        
        # 총 개수 계산
        total = query.count()
        
        # 정렬 및 페이징
        items = query.order_by(Cosmetic.name.asc()).offset((page - 1) * size).limit(size).all()
        
        # 결과를 딕셔너리 리스트로 변환
        result_items = []
        for item in items:
            result_items.append({
                'cosmetic_id': item.cosmetic_id,
                'name': item.name,
                'brand': item.brand,
                'category': item.category,
                'price': item.price,
                'file_path': item.file_path,
                'like_count': item.like_count or 0,
                'is_liked': item.is_liked or False
            })
        
        return result_items, total
