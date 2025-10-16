from sqlalchemy import Column, Integer
from .common import Base, Common

class SkinImage(Base, Common):
    __tablename__ = "skin_image"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=False)

