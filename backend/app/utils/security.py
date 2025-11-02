"""JWT 보안 설정 및 검증 유틸"""
import os
import jwt
from typing import Optional, Dict, Tuple
from fastapi import Request
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"

# 화이트리스트 경로 (JWT 검증 제외)
PUBLIC_PATHS = [
    "/api",  # 서버 확인용 (정확히 /api만)
    "/api/health",  # 헬스 체크
    "/docs",  # Swagger UI
    "/openapi.json",  # Swagger JSON
    "/media",  # 정적 파일 서빙
]


def is_public_path(path: str) -> bool:
    """
    경로가 공개 경로인지 확인
    
    - 정확히 일치하는 경로: /api, /docs 등
    - 시작하는 경로: /api/health, /media 등
    """
    for public_path in PUBLIC_PATHS:
        # 정확히 일치하는 경우
        if path == public_path:
            return True
        # 경로로 시작하는 경우 (단, /api만 예외 처리)
        if public_path == "/api":
            # /api는 정확히 일치하는 경우만 공개
            continue
        if path.startswith(public_path):
            return True
    return False


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Authorization 헤더에서 Bearer 토큰 추출"""
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    return authorization[7:].strip()


def validate_and_decode_token(token: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    JWT 토큰 검증 및 디코딩을 한 번에 수행
    
    Returns:
        (is_valid, error_code, claims):
        - (True, None, claims): 유효한 토큰
        - (False, "TOKEN_EXPIRED", None): 만료된 토큰
        - (False, "INVALID_TOKEN", None): 잘못된 토큰
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        claims = {
            "memberId": int(payload.get("sub", 0)),
            "role": payload.get("role", ""),
            "type": payload.get("type", "")
        }
        return True, None, claims
    except jwt.ExpiredSignatureError:
        return False, "TOKEN_EXPIRED", None
    except jwt.InvalidTokenError:
        return False, "INVALID_TOKEN", None


def get_current_user(request: Request) -> Dict:
    """현재 사용자 정보 추출 (의존성 주입 함수)"""
    return {
        "member_id": getattr(request.state, "member_id", None),
        "role": getattr(request.state, "role", None)
    }

