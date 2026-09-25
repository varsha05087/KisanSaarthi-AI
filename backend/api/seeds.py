from typing import Optional
from fastapi import APIRouter, Query
from models.seed import SeedBookingRequest
from models.request import NotImplementedResponse

router = APIRouter(prefix="/api/seeds", tags=["Seeds & Agri Inputs"])


@router.get("", response_model=NotImplementedResponse, summary="Search available certified seeds and input centers")
async def list_seeds(
    crop: Optional[str] = Query(None, description="Crop name (e.g. Paddy, Cotton)"),
    location: Optional[str] = Query(None, description="Village / Mandal / District"),
    season: Optional[str] = Query(None, description="Season (e.g. Kharif, Rabi)"),
):
    """
    Queries certified seed varieties, RSK availability, and cooperative centers.
    Validates query parameters and returns placeholder contract response.
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/seeds",
    )


@router.post("/request", response_model=NotImplementedResponse, summary="Submit seed procurement assistance request")
async def request_seed(payload: SeedBookingRequest):
    """
    Submits a seed booking or RSK center reservation request.
    Validates booking schema and returns placeholder contract response.
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/seeds/request",
    )
