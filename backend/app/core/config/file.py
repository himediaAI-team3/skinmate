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
# static 폴더 경로 (로컬 또는 네트워크 공유 폴더)
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static"))

# 업로드 디렉토리 절대 경로
def get_upload_path() -> str:
    """업로드 디렉토리 경로 반환 (자동 생성)"""
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_static_file_url(file_path: str) -> str:
    """
    정적 파일 URL 생성 (상대 경로)
    
    Args:
        file_path: 파일 경로 (예: "cosmetic/1.jpg")
        
    Returns:
        상대 경로 (예: "/media/cosmetic/1.jpg")
        
    Note:
        프론트엔드에서는 현재 접속한 서버 주소와 조합하여 사용:
        `${window.location.origin}${file_path}`
        /media 경로는 main.py에서 STATIC_DIR로 마운트됨
    """
    if not file_path:
        return None
    
    # 경로를 정리 (앞뒤 공백 제거, 경로 구분자 정리)
    clean_path = file_path.strip().replace("\\", "/")
    
    # /media 접두사 추가하여 반환
    return f"/media/{clean_path}"


# 향후 확장 예시 (현재는 주석으로만 예시)
# def get_member_image_url(file_name: str) -> str:
#     """회원 프로필 이미지 URL 생성"""
#     if not file_name:
#         return None
#     clean_name = file_name.strip().replace("\\", "/")
#     return f"/media/members/{clean_name}"
# 
# def get_review_image_url(file_name: str) -> str:
#     """리뷰 이미지 URL 생성"""
#     if not file_name:
#         return None
#     clean_name = file_name.strip().replace("\\", "/")
#     return f"/media/reviews/{clean_name}"

