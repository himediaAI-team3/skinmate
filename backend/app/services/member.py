from sqlalchemy.orm import Session
from fastapi import status
from app.repository.member import MemberRepository
from app.schemas.member import MemberCreate
from app.models.member import Member
from app.core.exception import ApiException


class MemberService:
    
    @staticmethod
    def exists(db: Session, member_id: int) -> bool:
        """회원 존재 여부 확인"""
        return MemberRepository.exists(db, member_id)
    
    @staticmethod
    def get_member(db: Session, member_id: int) -> Member:
        """회원 정보 조회"""
        member = MemberRepository.get_by_id(db, member_id)
        if member is None:
            raise ApiException(status.HTTP_404_NOT_FOUND, "회원을 찾을 수 없습니다")
        return member
    
    @staticmethod
    def update_member(db: Session, member_id: int, data: MemberCreate) -> Member:
        # 회원 존재 여부 확인
        if not MemberRepository.exists(db, member_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "회원을 찾을 수 없습니다")
        
        # 데이터 변환 (dict로 변환: immutable → mutable)
        update_data = data.model_dump()
        update_data["updated_id"] = member_id  # 수정자 ID (현재 접속자 ID)
        
        # Repository 호출
        updated_member = MemberRepository.update(db, member_id, update_data)
        
        return updated_member
