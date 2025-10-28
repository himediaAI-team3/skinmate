import os
from pathlib import Path

# 파일업로드 관련 공통 설정

# 업로드 디렉토리 (환경변수 또는 기본값)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# 허용 파일 확장자
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 최대 파일 크기 (기본: 10MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # bytes

# 파일 서빙 관련 설정
# 화장품 이미지 폴더 경로 (로컬 또는 네트워크 공유 폴더)
# 17번 줄을 다음과 같이 수정
COSMETIC_IMAGE_DIR = os.getenv("COSMETIC_IMAGE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static", "cosmetic"))

# 파일 베이스 URL (환경변수로 설정 가능, 기본값은 로컬호스트)
FILE_BASE_URL = os.getenv("FILE_BASE_URL", "http://localhost:8000")

# 업로드 디렉토리 절대 경로
def get_upload_path() -> str:
    """업로드 디렉토리 경로 반환 (자동 생성)"""
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_file_url(file_name: str) -> str:
    """
    파일명을 전체 URL로 변환
    
    Args:
        file_name: 파일명 (예: "199.jpg")
        
    Returns:
        전체 URL (예: "http://localhost:8000/static/cosmetics/199.jpg")
    """
    if not file_name:
        return None
    
    # 파일명을 정리 (앞뒤 공백 제거, 경로 구분자 정리)
    clean_name = file_name.strip().replace("\\", "/")
    
    # 전체 URL 생성
    return f"{FILE_BASE_URL.rstrip('/')}/static/cosmetics/{clean_name}"

