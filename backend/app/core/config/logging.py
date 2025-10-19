import logging
import sys
from rich.logging import RichHandler

# Rich 핸들러로 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        rich_tracebacks=True,  # 에러 트레이스 예쁘게
        markup=True,           # 마크업 지원
        show_time=True,        # 시간 표시
        show_level=True,       # 레벨 표시
        show_path=True         # 파일 경로 표시
    )]
)

# 로거 생성 함수
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
