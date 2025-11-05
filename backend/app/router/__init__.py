from .member import router as member_router
from .analysis import router as analysis_router
from .file import router as file_router
from .like import router as like_router
from .cosmetic import router as cosmetic_router
from .test import router as test_router
from .chat import router as chat_router

__all__ = [
    "member_router",
    "analysis_router",
    "file_router",
    "like_router",
    "cosmetic_router",
    "test_router",
    "chat_router",
]

