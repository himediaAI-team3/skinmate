from fastapi import APIRouter, Query
import jwt
from datetime import datetime, timedelta
from app.utils.security import JWT_SECRET, JWT_ALGORITHM

router = APIRouter(prefix="/api", tags=["test"])

@router.get("/test-token")
async def generate_test_token(
    member_id: int = Query(1, description="회원 ID"),
    role: str = Query("USER", description="권한")
):
    """
    개발 환경용 테스트 JWT 토큰 생성
    
    - member_id: 회원 ID (기본값: 1)
    - role: 권한 (기본값: USER)
    """
    now = datetime.utcnow()
    expiry = now + timedelta(minutes=15)  # 15분
    
    iat_timestamp = int(now.timestamp())
    exp_timestamp = int(expiry.timestamp())
    
    payload = {
        "sub": str(member_id),  # Spring Boot와 동일하게 문자열로 저장
        "role": role,
        "type": "access",
        "iat": iat_timestamp,
        "exp": exp_timestamp
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "token": token,
        "message": "테스트 토큰이 생성되었습니다. Swagger UI의 Authorize에 입력하세요.",
        "format": f"Bearer {token}",
        "payload": payload
    }

