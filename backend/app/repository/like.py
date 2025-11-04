from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from app.models.like import Like
from app.models.cosmetic import Cosmetic
from app.models.file import File
from app.models.entity_type import EntityType
from app.core.config.file import get_static_file_url


class LikeRepository:
    @staticmethod
    def toggle_like(db: Session, member_id: int, cosmetic_id: int) -> dict:
        """
        좋아요 토글: INSERT 시도 → UNIQUE 위반 시 DELETE
        """
        try:
            # 1. 좋아요 추가 시도 (INSERT)
            like = Like(member_id=member_id, cosmetic_id=cosmetic_id)
            db.add(like)
            db.commit()
            db.refresh(like)
            return {"is_liked": True}
        except IntegrityError:
            # 2. UNIQUE 제약 위반 = 이미 좋아요 존재 → DELETE (취소)
            db.rollback()
            db.query(Like).filter(
                Like.member_id == member_id,
                Like.cosmetic_id == cosmetic_id
            ).delete()
            db.commit()
            return {"is_liked": False}

    @staticmethod
    def count_by_cosmetic(db: Session, cosmetic_id: int) -> int:
        """화장품별 좋아요 개수 조회"""
        return db.query(func.count(Like.like_id)).filter(
            Like.cosmetic_id == cosmetic_id
        ).scalar() or 0

    @staticmethod
    def is_liked_by_member(db: Session, member_id: int, cosmetic_id: int) -> bool:
        """회원이 특정 화장품을 좋아요했는지 확인"""
        return db.query(Like).filter(
            Like.member_id == member_id,
            Like.cosmetic_id == cosmetic_id
        ).first() is not None

    @staticmethod
    def get_like_info(db: Session, member_id: int, cosmetic_id: int) -> dict:
        """좋아요 여부와 개수 조회"""
        is_liked = LikeRepository.is_liked_by_member(db, member_id, cosmetic_id)
        like_count = LikeRepository.count_by_cosmetic(db, cosmetic_id)
        return {"is_liked": is_liked, "like_count": like_count}

    @staticmethod
    def count_liked_cosmetics_by_member(db: Session, member_id: int) -> int:
        """회원이 좋아요한 화장품 전체 개수 조회"""
        return db.query(func.count(Like.like_id)).filter(
            Like.member_id == member_id
        ).scalar() or 0

    @staticmethod
    def get_liked_cosmetics_with_pagination(db: Session, member_id: int, page: int = 1, size: int = 5) -> List[dict]:
        """좋아요한 화장품 목록 조회 (페이징)"""
        offset = (page - 1) * size
        
        # 서브쿼리: 대표 이미지 file_path
        file_path_sq = select(File.file_path).where(
            File.entity_type == EntityType.COSMETIC,
            File.entity_id == Cosmetic.cosmetic_id
        ).order_by(File.file_id.asc()).limit(1).scalar_subquery()
        
        # 메인 쿼리: LIKE JOIN COSMETIC JOIN FILE
        query = db.query(
            Cosmetic.cosmetic_id,
            Cosmetic.name,
            Cosmetic.brand,
            Cosmetic.price,
            file_path_sq.label('file_path')
        ).join(
            Like, Like.cosmetic_id == Cosmetic.cosmetic_id
        ).filter(
            Like.member_id == member_id
        )
        
        # 페이징
        results = query.order_by(Cosmetic.name.asc()).offset(offset).limit(size).all()
        
        # 결과를 딕셔너리 리스트로 변환
        items = []
        for row in results:
            items.append({
                'cosmetic_id': row.cosmetic_id,
                'name': row.name,
                'brand': row.brand,
                'price': row.price,
                'file_path': get_static_file_url(row.file_path),
                'is_liked': True
            })
        
        return items

