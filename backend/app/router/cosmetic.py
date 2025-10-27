from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.services.cosmetic import CosmeticService
from app.schemas.cosmetic import CosmeticSearchResponse, CosmeticSearchParams
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/cosmetics", tags=["cosmetics"])


@router.get("", response_model=ApiResponse)
def search_cosmetics(
    params: CosmeticSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """화장품 목록 검색"""
    
    # 서비스 호출
    result = CosmeticService.search_cosmetics(db=db, params=params)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="화장품 목록 조회 성공",
        data=result
    )
