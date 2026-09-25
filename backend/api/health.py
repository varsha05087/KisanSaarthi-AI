from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service Health Check")
async def health_check():
    """
    Returns backend service health status.
    Used for uptime checks and local verification.
    """
    return {
        "status": "ok",
        "service": "kisansaarthi-backend"
    }
