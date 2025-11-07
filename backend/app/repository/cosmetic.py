from sqlalchemy.orm import Session
from sqlalchemy import func, select, literal
from typing import List, Tuple, Optional
from app.models.cosmetic import Cosmetic
from app.models.like import Like
from app.models.file import File
from app.models.entity_type import EntityType
from app.core.config.file import get_static_file_url


class CosmeticRepository:
    
    @staticmethod
    def exists(db: Session, cosmetic_id: int) -> bool:
        """화장품 존재 여부 확인"""
        return db.query(Cosmetic).filter(Cosmetic.cosmetic_id == cosmetic_id).count() > 0
    
    @staticmethod
    def get_by_ids(db: Session, cosmetic_ids: List[int]) -> List[Cosmetic]:
        """
        여러 화장품 ID로 조회 (RAG 파이프라인용)
        Qdrant Vector 검색 Top 10 → MySQL 상세 정보 → LLM 최종 선정
        
        Args:
            db: 데이터베이스 세션
            cosmetic_ids: 화장품 ID 리스트
            
        Returns:
            List[Cosmetic]: 화장품 객체 리스트
        """
        return db.query(Cosmetic).filter(Cosmetic.cosmetic_id.in_(cosmetic_ids)).all()
    
    @staticmethod
    def get_all(db: Session) -> List[Cosmetic]:
        """
        모든 화장품 조회
        
        Returns:
            List[Cosmetic]: 화장품 객체 리스트
        """
        return db.query(Cosmetic).all()
    
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
                'file_path': get_static_file_url(item.file_path),
                'like_count': item.like_count or 0,
                'is_liked': item.is_liked or False
            })
        
        return result_items, total
    
    @staticmethod
    def get_detail(db: Session, cosmetic_id: int, member_id: Optional[int] = None) -> Optional[dict]:
        """화장품 상세 정보 조회"""
        
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
        
        # 메인 쿼리 - 모든 필드 조회
        result = db.query(
            Cosmetic.cosmetic_id,
            Cosmetic.name,
            Cosmetic.brand,
            Cosmetic.category,
            Cosmetic.price,
            Cosmetic.short_description,
            Cosmetic.description,
            Cosmetic.buy_url,
            Cosmetic.skin_type,
            Cosmetic.skin_disease,
            Cosmetic.main_effect,
            Cosmetic.care_symptom,
            Cosmetic.key_ingredient,
            Cosmetic.ingredients,
            file_path_sq.label('file_path'),
            like_count_sq.label('like_count'),
            is_liked_sq.label('is_liked')
        ).filter(Cosmetic.cosmetic_id == cosmetic_id).first()
        
        if not result:
            return None
        
        # 결과를 딕셔너리로 변환
        return {
            'cosmetic_id': result.cosmetic_id,
            'name': result.name,
            'brand': result.brand,
            'category': result.category,
            'price': result.price,
            'short_description': result.short_description,
            'description': result.description,
            'buy_url': result.buy_url,
            'skin_type': result.skin_type,
            'skin_disease': result.skin_disease,
            'main_effect': result.main_effect,
            'care_symptom': result.care_symptom,
            'key_ingredient': result.key_ingredient,
            'ingredients': result.ingredients,
            'file_path': get_static_file_url(result.file_path),
            'like_count': result.like_count or 0,
            'is_liked': result.is_liked or False
        }

    @staticmethod
    def get_basic_by_id(db: Session, cosmetic_id: int) -> Optional[dict]:
        """기본 컬럼만 조회 (LLM 프롬프트 입력용)""" # LLM 생성값으로 기존 6개 컬럼 덮어쓰기
        row = db.query(
            Cosmetic.cosmetic_id,
            Cosmetic.name,
            Cosmetic.brand,
            Cosmetic.category,
            Cosmetic.price,
            Cosmetic.ingredients,
            Cosmetic.short_description,
            Cosmetic.buy_url,
        ).filter(Cosmetic.cosmetic_id == cosmetic_id).first()

        if not row:
            return None

        return {
            'cosmetic_id': row.cosmetic_id,
            'name': row.name or '',
            'brand': row.brand or '',
            'category': row.category or '',
            'price': row.price,
            'ingredients': row.ingredients or '',
            'short_description': row.short_description or '',
            'buy_url': row.buy_url or '',
        }

    @staticmethod
    def upsert_llm_fields_mysql(
        db: Session,
        cosmetic_id: int,
        data: dict,
        overwrite: bool = True
    ) -> Cosmetic:
        """  # LLM 생성값으로 기존 6개 컬럼 덮어쓰기
        MySQL 기반 업서트: 존재하면 갱신, 없으면 생성
        - 항상 6개 컬럼을 새 값으로 덮어쓰기
        """

        obj = db.query(Cosmetic).filter(Cosmetic.cosmetic_id == cosmetic_id).first()

        # 대상 필드만 사용
        new_values = {
            'skin_type': data.get('skin_type'),
            'skin_disease': data.get('skin_disease'),
            'main_effect': data.get('main_effect'),
            'care_symptom': data.get('care_symptom'),
            'key_ingredient': data.get('key_ingredient'),
            'description': data.get('description'),
        }

        if obj:
            # 존재 시: 항상 새 값으로 덮어쓰기
            for k, v in new_values.items():
                setattr(obj, k, v)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

        # 없으면 새로 생성 (스텁 + 6개 컬럼)
        obj = Cosmetic(
            cosmetic_id=cosmetic_id,
            skin_type=new_values['skin_type'],
            skin_disease=new_values['skin_disease'],
            main_effect=new_values['main_effect'],
            care_symptom=new_values['care_symptom'],
            key_ingredient=new_values['key_ingredient'],
            description=new_values['description'],
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj