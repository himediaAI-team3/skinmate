from sqlalchemy import Column, Integer, String
from .common import Base, Common

class SkinAnalysis(Base, Common):
    __tablename__ = "skin_analysis"

    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=True)
    skin_type = Column(String(50), nullable=True)
    min_price = Column(Integer, nullable=True)
    max_price = Column(Integer, nullable=True)
