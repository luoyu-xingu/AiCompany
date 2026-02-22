from .audio import router as audio_router
from .chat import router as chat_router
from .config import router as config_router

__all__ = ["audio_router", "chat_router", "config_router"]
