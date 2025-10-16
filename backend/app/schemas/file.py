from sqlalchemy import Column, Integer, String
from .common import Base, Common

class File(Base, Common):
    __tablename__ = "file"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_url = Column(String(255), nullable=False)
    file_name = Column(String(255))
    mime_type = Column(String(100))
    size = Column(Integer)
    ref_id = Column(Integer, nullable=False)  # 0: cosmetic, 1: skin_image
    ref_pk = Column(Integer, nullable=False)  # 참조하는 테이블의 PK

