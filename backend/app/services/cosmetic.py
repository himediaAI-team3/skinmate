from sqlalchemy.orm import Session
from typing import Optional
from fastapi import status
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticSearchResponse, CosmeticSearchItem, CosmeticDetailResponse
from app.core.exception import ApiException


class CosmeticService:
    
    @staticmethod
    def search_cosmetics(
        db: Session,
        brand: Optional[str] = None,
        name: Optional[str] = None,
        skin_type: Optional[str] = None,
        category: Optional[str] = None,
        member_id: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> CosmeticSearchResponse:
        """화장품 목록 검색"""
        
        # 리포지토리에서 데이터 조회
        items_data, total = CosmeticRepository.search(
            db=db,
            brand=brand,
            name=name,
            skin_type=skin_type,
            category=category,
            member_id=member_id,
            page=page,
            size=size
        )
        
        # 스키마로 변환
        items = [CosmeticSearchItem(**item) for item in items_data]
        
        return CosmeticSearchResponse(
            page=page,
            size=size,
            total=total,
            items=items
        )
    
    @staticmethod
    def get_cosmetic_detail(
        db: Session,
        cosmetic_id: int,
        member_id: Optional[int] = None
    ) -> CosmeticDetailResponse:
        """화장품 상세 정보 조회"""
        
        # 리포지토리에서 데이터 조회
        data = CosmeticRepository.get_detail(db, cosmetic_id, member_id)
        
        # 데이터가 없으면 404 에러
        if not data:
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
        
        # 스키마로 변환하여 반환
        return CosmeticDetailResponse(**data)
