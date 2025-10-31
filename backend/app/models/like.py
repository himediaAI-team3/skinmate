from sqlalchemy import Column, Integer, UniqueConstraint, Index
from .common import Base, Common

class Like(Base, Common):
    __tablename__ = "like"

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=True)
    cosmetic_id = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('member_id', 'cosmetic_id', name='unique_member_cosmetic'),
        Index('idx_cosmetic_id', 'cosmetic_id'),
        Index('idx_member_id', 'member_id'),
    )
