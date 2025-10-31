from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.services.member import MemberService
from app.schemas.member import MemberCreate, MemberResponse
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/members", tags=["members"])


@router.put("/{member_id}", response_model=ApiResponse)
def update_member(member_id: int, data: MemberCreate, db: Session = Depends(get_db)):
    # Service 호출
    updated_member = MemberService.update_member(db, member_id, data)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="회원 정보가 업데이트되었습니다",
        data=MemberResponse.from_orm(updated_member)
    )

