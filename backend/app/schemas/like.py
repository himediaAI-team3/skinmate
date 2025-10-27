from pydantic import BaseModel


class LikeToggleRequest(BaseModel):
    """좋아요 토글 요청"""
    member_id: int


class LikeToggleResponse(BaseModel):
    """좋아요 토글 응답"""
    is_liked: bool
    like_count: int


class LikeCountResponse(BaseModel):
    """좋아요 개수 응답"""
    like_count: int


class LikeStatusResponse(BaseModel):
    """좋아요 상태 응답 (여부 + 개수)"""
    is_liked: bool
    like_count: int
