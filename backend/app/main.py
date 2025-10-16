from fastapi import FastAPI
import uvicorn
from app.core.config.database import engine
from app.schemas import Base
from app.router import skin_image

# FastAPI 애플리케이션 생성 (Swagger 표시 설정)
app = FastAPI(
    title="SkinMate API",
    description="피부질환 진단 및 화장품 추천 서비스 API",
    docs_url= "/docs"
)

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "SkinMate API 서버 실행 성공"}

# 헬스 체크 엔드포인트
@app.get("/health")
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
