from sqlalchemy import Column, Integer, String
from .common import Base, Common

class Member(Base, Common):
    __tablename__ = "member"

    member_id = Column(Integer, primary_key=True, autoincrement=True)

    oauth_provider = Column(String(50), nullable=True)  # google, kakao, naver
    oauth_id = Column(String(100), nullable=True)

    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    role = Column(String(20), nullable=True, default="USER")

    skin_type = Column(String(50), nullable=True)           # 건성, 지성, 복합성, 민감성 등
    gender = Column(String(10), nullable=True)              # 성별
    age_group = Column(Integer, nullable=True)           # 나이대

