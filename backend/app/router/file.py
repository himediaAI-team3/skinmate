from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config.database import get_db
from app.repository.file import FileRepository
from app.core.exception import ApiException
import os

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/{file_id}")
def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):

    # 파일 조회
    file = FileRepository.get_by_id(db, file_id)
    
    if not file:
        raise ApiException(status.HTTP_404_NOT_FOUND, "파일을 찾을 수 없습니다")
    
    # 파일 존재 확인
    file_path = file.file_path.lstrip("\\")  # "/uploads/xxx.jpg" → "uploads/xxx.jpg"
    
    if not os.path.exists(file_path):
        raise ApiException(status.HTTP_404_NOT_FOUND, "파일이 존재하지 않습니다")
    
    # 파일 반환
    return FileResponse(
        path=file_path,
        media_type=file.mime_type,
        # filename=file.file_name
    )

