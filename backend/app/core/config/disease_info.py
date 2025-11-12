"""
질환 정보 파일 경로 설정
"""
import os
from pathlib import Path

# 질환 정보 파일 디렉토리
BASE_DIR = Path(__file__).parent.parent.parent.parent
DISEASE_INFO_DIR = os.path.join(BASE_DIR, "data")

# 질환 파일명 목록
DISEASE_FILES = [
    "아토피.txt",
    "여드름.txt",
    "건선.txt",
    "주사.txt",
    "지루.txt",
]


def get_disease_info_dir() -> str:
    """질환 정보 파일 디렉토리 경로 반환"""
    return DISEASE_INFO_DIR


def get_disease_file_path(disease_file_name: str) -> str:
    """질환 정보 파일 전체 경로 반환"""
    return os.path.join(DISEASE_INFO_DIR, disease_file_name)

