from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from .common import Base, Common
from .entity_type import EntityType

class File(Base, Common):
    __tablename__ = "file"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(SQLEnum(EntityType), nullable=True)
    entity_id = Column(Integer, nullable=True)
    file_path = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=True)

