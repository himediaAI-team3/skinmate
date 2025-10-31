from sqlalchemy import Column, Integer
from .common import Base, Common

class SkinAnalysis(Base, Common):
    __tablename__ = "skin_analysis"

    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=True)

