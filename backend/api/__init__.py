"""
API routers package for KisanSaarthi AI.
"""

from api.health import router as health_router
from api.chat import router as chat_router
from api.voice import router as voice_router
from api.crop import router as crop_router
from api.tractors import router as tractors_router
from api.insurance import router as insurance_router
from api.seeds import router as seeds_router
from api.requests import router as requests_router
from api.farmers import router as farmers_router

__all__ = [
    "health_router",
    "farmers_router",
    "chat_router",
    "voice_router",
    "crop_router",
    "tractors_router",
    "insurance_router",
    "seeds_router",
    "requests_router",
]
