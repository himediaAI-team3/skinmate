from sqlalchemy import Column, Integer, String
from .common import Base, Common

class File(Base, Common):
    __tablename__ = "file"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_url = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=True)
    ref_type = Column(String(30), nullable=True)
    ref_pk = Column(Integer, nullable=True)

