from sqlalchemy.orm import Session
from app.models.member import Member

class MemberRepository:
    
    @staticmethod
    def exists(db: Session, member_id: int) -> bool:
        return db.query(Member).filter(Member.member_id == member_id).count() > 0
    
    @staticmethod
    def update(db: Session, member_id: int, update_data: dict) -> Member:
    
        # UPDATE 쿼리 실행
        db.query(Member).filter(Member.member_id == member_id).update(update_data)
        db.commit()
    
        # 업데이트된 데이터 조회
        member = db.query(Member).filter(Member.member_id == member_id).first()
        return member
