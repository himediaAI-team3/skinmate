from sqlalchemy.orm import Session
from typing import Optional
from fastapi import status
from app.core.exception import ApiException
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticSearchParams, CosmeticSearchResponse, CosmeticSearchItem, CosmeticDetailResponse


class CosmeticService:
    
    @staticmethod
    def search_cosmetics(
        db: Session,
        params: CosmeticSearchParams
    ) -> CosmeticSearchResponse:
        """화장품 목록 검색"""
        
        # 리포지토리에서 데이터 조회
        items_data, total = CosmeticRepository.search(
            db=db,
            brand=params.brand,
            name=params.name,
            skin_type=params.skin_type,
            category=params.category,
            member_id=params.member_id,
            page=params.page,
            size=params.size
        )
        
        # 스키마로 변환
        items = [CosmeticSearchItem(**item) for item in items_data]
        
        return CosmeticSearchResponse(
            page=params.page,
            size=params.size,
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
