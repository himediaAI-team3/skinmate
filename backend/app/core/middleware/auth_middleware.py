"""JWT 인증 미들웨어"""
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.security import is_public_path, extract_bearer_token, validate_and_decode_token


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT 검증 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        # 공개 경로는 검증 제외
        if is_public_path(request.url.path):
            return await call_next(request)
        
        # Authorization 헤더에서 토큰 추출
        authorization = request.headers.get("Authorization")
        token = extract_bearer_token(authorization)
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "code": 401,
                    "success": False,
                    "message": "토큰이 필요합니다",
                    "data": None
                }
            )
        
        # 토큰 검증 및 디코딩(claims 추출: memberId and role)
        is_valid, error_code, claims = validate_and_decode_token(token)
        if not is_valid:
            if error_code == "TOKEN_EXPIRED":
                message = "토큰이 만료되었습니다"
            else:  # INVALID_TOKEN
                message = "유효하지 않은 토큰입니다"
            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "code": 401,
                    "error_code": error_code,
                    "success": False,
                    "message": message,
                    "data": None
                }
            )
        
        # request.state에 저장
        request.state.member_id = claims["memberId"]
        request.state.role = claims["role"]
        
        return await call_next(request)

