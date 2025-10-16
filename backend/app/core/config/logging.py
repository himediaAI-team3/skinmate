import logging
import sys
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로그 레벨 설정 (환경변수에서 가져오거나 기본값 INFO 사용)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# 로그 포맷 설정
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 기본 로거 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 로거 생성
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
