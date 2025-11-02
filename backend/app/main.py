from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.core.config.database import lifespan
from app.core.config.file import STATIC_DIR
from app.core.exception import ApiException, api_exception_handler
from app.core.middleware.auth_middleware import JWTMiddleware
from app.router import member_router, analysis_router, file_router, like_router, cosmetic_router
from fastapi.middleware.cors import CORSMiddleware

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

# JWT 검증 미들웨어 등록
app.add_middleware(JWTMiddleware)

# 전역 예외 핸들러 등록
app.add_exception_handler(ApiException, api_exception_handler)

# 라우터 등록
app.include_router(member_router)
app.include_router(analysis_router)
app.include_router(file_router)
app.include_router(like_router)
app.include_router(cosmetic_router)

# 정적 파일 서빙 - /media 경로로 마운트 (업로드된 미디어 파일)
app.mount("/media", StaticFiles(directory=STATIC_DIR), name="media")

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
