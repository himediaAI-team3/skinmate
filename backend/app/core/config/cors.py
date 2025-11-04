"""CORS 설정"""

def get_cors_config() -> dict:
    """CORS 설정 반환"""
    return {
        "allow_origins": ["*"],  # ex ["http://localhost:3000", "http://192.168.0.249:3000"]
        "allow_credentials": True,
        "allow_methods": ["*"],  # GET, POST, PUT, DELETE, OPTIONS 전부 허용
        "allow_headers": ["*"]  # 모든 헤더 허용
    }

