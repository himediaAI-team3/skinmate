from sqlalchemy import Column, Integer, String, DECIMAL
from .common import Base, Common

class Recommendation(Base, Common):
    __tablename__ = "recommendation"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=False)
    diagnosis_id = Column(Integer, nullable=False)
    cosmetic_id = Column(Integer, nullable=False)
    reason = Column(String(255))

