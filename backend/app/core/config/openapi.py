"""OpenAPI 스키마 커스터마이징"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# 공개 경로 (Swagger UI에서 security 제외)
PUBLIC_PATHS = {"/api", "/api/health", "/api/test-token", "/docs", "/openapi.json"}


def custom_openapi(app: FastAPI):
    """OpenAPI 스키마에 JWT Bearer 인증 추가"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Bearer JWT 인증 스키마 추가
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # 모든 경로에 Bearer 인증 추가 (공개 경로 제외)
    for path_key in openapi_schema["paths"]:
        if path_key in PUBLIC_PATHS or path_key.startswith("/media"):
            continue
        for method in openapi_schema["paths"][path_key]:
            if method not in ["parameters"]:
                if "security" not in openapi_schema["paths"][path_key][method]:
                    openapi_schema["paths"][path_key][method]["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

