from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, foreign
from .common import Base, Common

class Recommendation(Base, Common):
    __tablename__ = "recommendation"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=True)
    cosmetic_id = Column(Integer, nullable=True)
    reason = Column(String(255), nullable=True)
    ranking = Column(Integer, nullable=True)
    
    # Relationship 추가 (외래 키 제약 없이)
    cosmetic = relationship(
        "Cosmetic",
        primaryjoin="Recommendation.cosmetic_id == foreign(Cosmetic.cosmetic_id)",
        foreign_keys="[Recommendation.cosmetic_id]",
        uselist=False,
        viewonly=True
    )

