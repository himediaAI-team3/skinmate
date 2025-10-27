from sqlalchemy.orm import Session
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticSearchParams, CosmeticSearchResponse, CosmeticSearchItem


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
