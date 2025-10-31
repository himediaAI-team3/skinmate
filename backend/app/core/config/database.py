import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 데이터베이스 연결 정보 (기본값 설정)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "skinmate")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# MySQL 연결 URL 생성
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # 연결 풀 크기
    max_overflow=10,      # 초과 연결 허용 수
    echo=True            # SQL 로그 출력
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 세션 반환
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

