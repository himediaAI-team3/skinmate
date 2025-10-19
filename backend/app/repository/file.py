from sqlalchemy.orm import Session
from app.models.file import File


class FileRepository:
    
    @staticmethod
    def create(db: Session, file_data: dict) -> File:
        """파일 정보 저장"""
        file = File(**file_data)
        db.add(file)
        db.commit()
        db.refresh(file)
        return file
    
    @staticmethod
    def get_by_analysis_id(db: Session, analysis_id: int) -> File:
        return db.query(File).filter(File.analysis_id == analysis_id).first()
    

