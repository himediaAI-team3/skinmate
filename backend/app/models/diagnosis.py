from sqlalchemy import Column, Integer, String, Text
from .common import Base, Common

class Diagnosis(Base, Common):
    __tablename__ = "diagnosis"

    diagnosis_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, nullable=True)
    disease_name = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)

