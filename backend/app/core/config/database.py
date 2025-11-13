import os
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import FastAPI
# from app.models import Base
from sqlalchemy.exc import SQLAlchemyError

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
    echo=False            # SQL 로그 끄기 (에러는 여전히 출력됨)
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


"""
필수 테이블/뷰가 존재하는지 검사
누락된 객체가 있으면 RuntimeError를 발생시켜 애플리케이션 기동 중단
"""
def verify_schema() -> None:
    # 필수 테이블/뷰 목록
    REQUIRED_TABLES = {
        "member",
        "skin_analysis",
        "file",
        "diagnosis",
        "cosmetic",
        "recommendation",
        "like",
    }

    REQUIRED_VIEWS = {
        "analysis_result_view",
    }
    
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        existing_views = set(inspector.get_view_names())
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "데이터베이스 스키마를 확인할 수 없습니다. DB 연결 설정 및 초기화 스크립트 실행을 확인하세요."
        ) from exc

    missing_tables = REQUIRED_TABLES - existing_tables
    missing_views = REQUIRED_VIEWS - existing_views

    if missing_tables or missing_views:
        missing_parts = []
        if missing_tables:
            missing_parts.append(f"tables: {', '.join(sorted(missing_tables))}")
        if missing_views:
            missing_parts.append(f"views: {', '.join(sorted(missing_views))}")

        raise RuntimeError(
            "데이터베이스 스키마가 초기화되지 않았습니다. "
            f"누락된 객체 -> {'; '.join(missing_parts)}. "
            "컨테이너 기동 시 실행되는 SQL 스크립트를 먼저 적용하세요."
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 lifecycle 함수"""

    # 시작 시 실행 - VIEW를 제외하고 테이블만 생성
    # tables_to_create = [
    #     table for table in Base.metadata.sorted_tables 
    #     if not table.info.get('is_view', False)
    # ]
    # Base.metadata.create_all(bind=engine, tables=tables_to_create)
    
    verify_schema()
    yield