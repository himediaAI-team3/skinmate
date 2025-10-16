from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .common import Common

Base = declarative_base()

class Member(Base, Common):
    __tablename__ = "member"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    oauth_provider = Column(String(50), nullable=False)  # google, kakao, naver
    oauth_id = Column(String(100), nullable=False)
    name = Column(String(100))
    email = Column(String(100))
    role = Column(String(20), default="USER")
    skin_type = Column(String(50), nullable=True)           # 건성, 지성, 복합성, 민감성 등
    min_price = Column(Integer, nullable=True) 
    max_price = Column(Integer, nullable=True) 

