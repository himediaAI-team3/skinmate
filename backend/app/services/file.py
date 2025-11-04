from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.repository.file import FileRepository
from app.models.file import File
from app.models.entity_type import EntityType
from app.core.config.file import get_upload_path, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
import os
import uuid


class FileService:
    
    @staticmethod
    def upload_and_save(db: Session, analysis_id: int, image_file: UploadFile) -> File:
        """
        이미지 파일 저장 및 DB INSERT
        
        Args:
            db: 데이터베이스 세션
            analysis_id: 분석 ID
            image_file: 업로드 파일
            
        Returns:
            File 객체
        """
        # 업로드 디렉토리 (설정에서 로드)
        upload_dir = get_upload_path()
        
        # 고유 파일명 생성: {analysis_id}_{uuid}.jpg
        file_ext = os.path.splitext(image_file.filename)[1]
        unique_filename = f"{analysis_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 실제 파일 저장
        with open(file_path, "wb") as f:
            f.write(image_file.file.read())
        
        file_data = {
            "entity_type": EntityType.SKIN_ANALYSIS,
            "entity_id": analysis_id,
            "file_path": file_path,
            "file_name": image_file.filename,
            "mime_type": image_file.content_type,
            "size": os.path.getsize(file_path)
        }
        
        # file 테이블 INSERT
        return FileRepository.create(db, file_data)

