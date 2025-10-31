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
    def update_member(db: Session, member_id: int, data: MemberCreate) -> Member:
        # 회원 존재 여부 확인
        if not MemberRepository.exists(db, member_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "회원을 찾을 수 없습니다")
        
        # 데이터 변환
        update_data = data.model_dump()
        
        # Repository 호출
        updated_member = MemberRepository.update(db, member_id, update_data)
        
        return updated_member

    @staticmethod
    def get_member(db: Session, member_id: int) -> Member | None:
        """회원 단건 조회 (추천 로직에서 사용자 속성 사용용)"""
        return db.query(Member).filter(Member.member_id == member_id).first()