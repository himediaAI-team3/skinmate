from sqlalchemy.orm import Session
from app.models.member import Member

class MemberRepository:
    
    @staticmethod
    def exists(db: Session, member_id: int) -> bool:
        return db.query(Member).filter(Member.member_id == member_id).count() > 0
    
    @staticmethod
    def get_by_id(db: Session, member_id: int) -> Member:
        """
        회원 ID로 조회
        회원 ID로 특정 회원의 정보를 데이터베이스에서 조회
        
        Args:
            db: DB 세션
            member_id: 회원 ID
            
        Returns:
            Member: 회원 객체 (없으면 None)
        """
        return db.query(Member).filter(Member.member_id == member_id).first()
    
    @staticmethod
    def update(db: Session, member_id: int, update_data: dict) -> Member:
    
        # UPDATE 쿼리 실행
        db.query(Member).filter(Member.member_id == member_id).update(update_data)
        db.commit()
    
        # 업데이트된 데이터 조회
        member = db.query(Member).filter(Member.member_id == member_id).first()
        return member
