from sqlalchemy import Column, Integer, String
from .common import Base, Common

class Recommendation(Base, Common):
    __tablename__ = "recommendation"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=True)
    cosmetic_id = Column(Integer, nullable=True)
    reason = Column(String(255), nullable=True)
    ranking = Column(Integer, nullable=True)

