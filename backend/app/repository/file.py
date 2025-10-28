from sqlalchemy.orm import Session
from app.models.file import File
from app.models.entity_type import EntityType


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
    def get_by_id(db: Session, file_id: int) -> File:
        """파일 ID로 조회"""
        return db.query(File).filter(File.file_id == file_id).first()
    
    @staticmethod
    def get_by_entity(db: Session, entity_type: EntityType, entity_id: int) -> File:
        """entity로 파일 조회"""
        return db.query(File).filter(
            File.entity_type == entity_type,
            File.entity_id == entity_id
        ).first()
    
    @staticmethod
    def delete_by_entity(db: Session, entity_type: EntityType, entity_id: int) -> bool:
        """entity로 파일 삭제"""
        file = db.query(File).filter(
            File.entity_type == entity_type,
            File.entity_id == entity_id
        ).first()
        
        if not file:
            return False
        
        db.delete(file)
        return True


