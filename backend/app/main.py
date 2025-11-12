from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.core.config.database import lifespan
from app.core.config.file import STATIC_DIR
from app.core.config.cors import get_cors_config
from app.core.config.openapi import custom_openapi
# from app.core.config import logging as _logging_config  # 로깅 설정 로드 (INFO 레벨 출력 활성화) - 개발 완료 후 비활성화
from app.core.exception import ApiException, api_exception_handler
from app.core.middleware.auth_middleware import JWTMiddleware
from app.router import member_router, analysis_router, file_router, like_router, cosmetic_router, test_router, chat_router
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 애플리케이션 생성 (Swagger 표시 설정)
app = FastAPI(
    title="SkinMate API",
    description="피부질환 진단 및 화장품 추천 서비스 API",
    docs_url="/docs",
    lifespan=lifespan
)

# OpenAPI 스키마 커스터마이징 설정(JWT Bearer 인증 테스트용)
app.openapi = lambda: custom_openapi(app)

# JWT 검증 미들웨어 등록
app.add_middleware(JWTMiddleware)

# CORS 설정
app.add_middleware(CORSMiddleware, **get_cors_config())

# 전역 예외 핸들러 등록
app.add_exception_handler(ApiException, api_exception_handler)

# 라우터 등록
app.include_router(member_router)
app.include_router(analysis_router)
app.include_router(file_router)
app.include_router(like_router)
app.include_router(cosmetic_router)
app.include_router(test_router)
app.include_router(chat_router)

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
