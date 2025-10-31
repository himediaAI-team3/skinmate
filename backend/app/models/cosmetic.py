from sqlalchemy import Column, Integer, String, Text, DECIMAL
from .common import Base, Common

class Cosmetic(Base, Common):
    __tablename__ = "cosmetic"

    cosmetic_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=True)
    brand = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    ingredients = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True, comment='한줄설명')
    description = Column(Text, nullable=True, comment='상세설명')
    buy_url = Column(String(2048), nullable=True)
    skin_type = Column(String(50), nullable=True, comment='피부타입')
    skin_disease = Column(String(50), nullable=True, comment='관련 피부질환')
    main_effect = Column(String(100), nullable=True, comment='주요효능')
    care_symptom = Column(String(100), nullable=True, comment='케어증상')
    key_ingredient = Column(String(200), nullable=True, comment='핵심성분')

