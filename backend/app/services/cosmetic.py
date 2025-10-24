from sqlalchemy.orm import Session
from typing import Optional
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticSearchResponse, CosmeticSearchItem


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
