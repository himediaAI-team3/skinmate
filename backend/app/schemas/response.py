from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    success : 요청 성공 여부
    code    : HTTP 상태 코드 또는 내부 코드
    message : 결과 설명 (성공/실패 사유)
    data    : 실제 응답 데이터 (Pydantic 객체, 리스트, dict 등) => JSON
    timestamp : 응답 시각
    """
    code: int
    success: bool
    message: str
    data: Optional[T] = None
    timestamp: datetime = datetime.utcnow()

    class Config:
        orm_mode = True