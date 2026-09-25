from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database.connection import init_db
from api import (
    health_router,
    farmers_router,
    chat_router,
    voice_router,
    crop_router,
    tractors_router,
    insurance_router,
    seeds_router,
    requests_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager.
    Initializes database tables in SQLite when server starts.
    Preserves all existing tables and data across restarts.
    """
    init_db()
    yield


# Initialize FastAPI application with metadata & database lifecycle
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic AI Backend for KisanSaarthi AI — Empowering farmers via Voice, Vision, and Actionable Agents.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for safe JSON error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred.",
            "detail": str(exc) if settings.APP_ENV == "development" else None,
        },
    )


# Include Feature Routers
app.include_router(health_router)
app.include_router(farmers_router)
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(crop_router)
app.include_router(tractors_router)
app.include_router(insurance_router)
app.include_router(seeds_router)
app.include_router(requests_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing quick navigation links."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/api/farmers",
            "/api/requests",
            "/api/tractors/book",
            "/api/chat",
            "/api/voice",
            "/api/crop/analyze",
            "/api/insurance/assist",
            "/api/seeds/request",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
