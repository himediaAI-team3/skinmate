from sqlalchemy import Column, Integer, Boolean, UniqueConstraint, Index
from .common import Base, Common

class Like(Base, Common):
    __tablename__ = "like"

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=True)
    cosmetic_id = Column(Integer, nullable=True)
    is_liked = Column(Boolean, nullable=True, default=True, comment='좋아요 여부 (1: 좋아요, 0: 좋아요 취소)')

    __table_args__ = (
        UniqueConstraint('member_id', 'cosmetic_id', name='unique_member_cosmetic'),
        Index('idx_cosmetic_id', 'cosmetic_id'),
        Index('idx_member_id', 'member_id'),
    )
