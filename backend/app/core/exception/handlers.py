"""전역 예외 핸들러"""
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from .exceptions import ApiException


def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
    """
    API 예외 핸들러
    
    ApiException 발생 시 App에의해 자동으로 호출되어
    ApiResponse 형식으로 변환하여 클라이언트에게 반환
    """
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "success": False,
            "message": exc.message,
            "data": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
