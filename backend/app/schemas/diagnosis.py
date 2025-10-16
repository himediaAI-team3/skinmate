from sqlalchemy import Column, Integer, String, Text
from .common import Base, Common

class Diagnosis(Base, Common):
    __tablename__ = "diagnosis"

    diagnosis_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=False)
    disease_name = Column(String(100), nullable=False)
    summary = Column(Text)

