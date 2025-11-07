class ApiException(Exception):
    """
    API 공통 커스텀 예외 정의
    
    Attributes:
        code: HTTP 상태 코드
        message: 에러 메시지
    """
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class VectorSearchException(ApiException):
    """벡터 검색 실패 예외"""
    pass


class LLMParsingException(ApiException):
    """LLM 응답 파싱 실패 예외"""
    pass
