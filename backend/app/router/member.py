from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict
from app.core.config.database import get_db
from app.services.member import MemberService
from app.schemas.member import MemberCreate, MemberResponse
from app.schemas.response import ApiResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/members", tags=["members"])

@router.get("/me", response_model=ApiResponse[MemberResponse])
def get_my_info(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    member_id = current_user["member_id"]
    member = MemberService.get_member(db, member_id)

    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="성공",
        data=MemberResponse.model_validate(member)
    )

@router.put("/me", response_model=ApiResponse)
def update_my_info(
    data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    member_id = current_user["member_id"]
    
    # Service 호출
    updated_member = MemberService.update_member(db, member_id, data)
    
    # ApiResponse로 감싸서 반환
    return ApiResponse(
        code=status.HTTP_200_OK,
        success=True,
        message="회원 정보가 업데이트되었습니다",
        data=MemberResponse.model_validate(updated_member) # SQLAlchemy 모델 → Pydantic 자동 변환 (역직렬화)
    )

