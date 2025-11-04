from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text
from .common import Base

class AnalysisResultView(Base):
    __tablename__ = "analysis_result_view"
    __table_args__ = {
        'info': dict(is_view=True),
        'extend_existing': True
    }
    
    analysis_id = Column(Integer, primary_key=True)
    member_id = Column(Integer)
    analysis_created_at = Column(DateTime)
    skin_file_id = Column(Integer)
    disease_name = Column(String(100))
    diagnosis_summary = Column(Text)
    cosmetic_id = Column(Integer, primary_key=True)
    cosmetic_name = Column(String(200))
    brand = Column(String(100))
    price = Column(DECIMAL(10, 2))
    buy_url = Column(String(2048))
    cosmetic_file_path = Column(String(255))
    reason = Column(String(255))
    ranking = Column(Integer)

