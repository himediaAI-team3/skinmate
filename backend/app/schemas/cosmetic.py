from sqlalchemy import Column, Integer, String, Text, DECIMAL
from .common import Base, Common

class Cosmetic(Base, Common):
    __tablename__ = "cosmetic"

    cosmetic_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(50))
    price = Column(DECIMAL(10, 2))
    ingredients = Column(Text)
    buy_url = Column(String(255))

