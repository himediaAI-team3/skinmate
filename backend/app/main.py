from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from app.core.config.database import engine
from app.models import Base
from app.core.exception import ApiException, api_exception_handler
from app.router import member_router, analysis_router, file_router
from fastapi.middleware.cors import CORSMiddleware


# 앱 시작 시 테이블 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    Base.metadata.create_all(bind=engine)
    yield
    # 종료 시 실행 (필요시)

# FastAPI 애플리케이션 생성 (Swagger 표시 설정)
app = FastAPI(
    title="SkinMate API",
    description="피부질환 진단 및 화장품 추천 서비스 API",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ex ["http://localhost:3000", "http://192.168.0.249:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS 전부 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 전역 예외 핸들러 등록
app.add_exception_handler(ApiException, api_exception_handler)

# 라우터 등록
app.include_router(member_router)
app.include_router(analysis_router)
app.include_router(file_router)

# 기본 라우트
@app.get("/api")
async def root():
    return {"message": "SkinMate API 서버 실행 성공"}

# 헬스 체크 엔드포인트
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SkinMate API"}

# SQLAlchemy 테이블 자동 생성
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
