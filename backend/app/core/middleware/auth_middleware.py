"""JWT 인증 미들웨어"""
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from app.utils.security import is_public_path, extract_bearer_token, validate_and_decode_token


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT 검증 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        # CORS preflight(OPTIONS) 요청은 인증 검증 없이 즉시 응답
        if request.method.upper() == "OPTIONS":
            origin = request.headers.get("origin")
            allow_headers = request.headers.get("access-control-request-headers", "*")
            headers = {
                "Access-Control-Allow-Origin": origin or "*",
                "Access-Control-Allow-Credentials": "true" if origin else "false",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS,PATCH",
                "Access-Control-Allow-Headers": allow_headers,
                "Vary": "Origin",
                "Access-Control-Max-Age": "86400",
            }
            return Response(status_code=status.HTTP_200_OK, headers=headers)
        
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
            elif error_code == "INVALID_SIGNATURE":
                message = "토큰 서명이 일치하지 않습니다."
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

