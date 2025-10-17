from sqlalchemy import Column, Integer, String, DECIMAL
from .common import Base, Common

class Recommendation(Base, Common):
    __tablename__ = "recommendation"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=True)
    diagnosis_id = Column(Integer, nullable=True)
    cosmetic_id = Column(Integer, nullable=True)
    reason = Column(String(255), nullable=True)
    ranking = Column(Integer, nullable=True)

