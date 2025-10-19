import os
from pathlib import Path

# 파일업로드 관련 공통 설정

# 업로드 디렉토리 (환경변수 또는 기본값)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# 허용 파일 확장자
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 최대 파일 크기 (기본: 10MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # bytes

# 업로드 디렉토리 절대 경로
def get_upload_path() -> str:
    """업로드 디렉토리 경로 반환 (자동 생성)"""
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

