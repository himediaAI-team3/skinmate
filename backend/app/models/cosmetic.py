from sqlalchemy import Column, Integer, String, Text, DECIMAL
from .common import Base, Common

class Cosmetic(Base, Common):
    __tablename__ = "cosmetic"

    cosmetic_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=True)
    brand = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    image_url = Column(String(255), nullable=True)
    ingredients = Column(Text, nullable=True)
    buy_url = Column(String(255), nullable=True)

