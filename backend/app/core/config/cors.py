"""CORS 설정"""

import os

# Vercel 프리뷰(브랜치) 도메인까지 임시 허용할지 여부 (원치 않으면 0)
ALLOW_VERCEL_PREVIEW = os.getenv("ALLOW_VERCEL_PREVIEW", "1") == "1"

def get_cors_config() -> dict:
    """CORS 설정 반환"""
    allow_origins = [
        "https://skinmate.site",
        "https://www.skinmate.site",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.249:3000",
    ]

    config = {
        "allow_origins": allow_origins,
        # 프리뷰 도메인 허용(원치 않으면 환경변수로 끄기)
        "allow_origin_regex": r"https://.*\.vercel\.app$" if ALLOW_VERCEL_PREVIEW else None,
        "allow_credentials": True,
        # ["*"] 도 가능하지만 명시해두는 편이 안전
        "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        # Authorization, Content-Type 등 포함 전부 허용
        "allow_headers": ["*"],
        # 브라우저 노출 헤더(필요 없으면 삭제 가능)
        "expose_headers": ["*"],
        # 프리플라이트 캐시(초)
        "max_age": 86400,
    }

    # None 값은 제거(Starlette가 None 키를 인자로 받지 않도록)
    return {k: v for k, v in config.items() if v is not None}
