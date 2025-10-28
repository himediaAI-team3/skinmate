from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
from app.core.config.database import engine
from app.core.config.file import COSMETIC_IMAGE_DIR
from app.models import Base
from app.core.exception import ApiException, api_exception_handler
from app.router import member_router, analysis_router, file_router, like_router, cosmetic_router
from fastapi.middleware.cors import CORSMiddleware


# 앱 시작 시 테이블 생성 (VIEW 제외)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행 - VIEW를 제외하고 테이블만 생성
    tables_to_create = [
        table for table in Base.metadata.sorted_tables 
        if not table.info.get('is_view', False)
    ]
    Base.metadata.create_all(bind=engine, tables=tables_to_create)
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
app.include_router(like_router)
app.include_router(cosmetic_router)

# 정적 파일 서빙 - 화장품 이미지를 /static/cosmetics 경로로 마운트
app.mount("/static/cosmetics", StaticFiles(directory=COSMETIC_IMAGE_DIR), name="cosmetic-images")

# 기본 라우트
@app.get("/api")
async def root():
    return {"message": "SkinMate API 서버 실행 성공"}

# 헬스 체크 엔드포인트
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SkinMate API"}

# 테이블 생성은 lifespan에서 처리됨 (VIEW 제외)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
