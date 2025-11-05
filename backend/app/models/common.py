from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Common:
    created_at = Column(DateTime, server_default=func.now())
    created_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    updated_id = Column(Integer, nullable=True)

