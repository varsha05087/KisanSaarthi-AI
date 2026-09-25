from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database import repository
from models.request import RequestCreate, RequestItemResponse

router = APIRouter(prefix="/api/requests", tags=["Farmer Requests"])


@router.get("", response_model=List[RequestItemResponse], summary="List farmer workflow requests from SQLite")
def list_requests(
    farmer_id: Optional[str] = Query(None, description="Filter requests by farmer identifier", examples=["F001"]),
    db: Session = Depends(get_db),
):
    """
    Retrieves all workflow requests created by a farmer from SQLite database.
    Returns an empty list [] if no requests exist for this farmer.
    """
    requests = repository.list_farmer_requests(db, farmer_id=farmer_id)
    return requests


@router.get("/{request_id}", response_model=RequestItemResponse, summary="Get details for a specific request from SQLite")
def get_request_by_id(
    request_id: str = Path(..., description="Unique request identifier", examples=["REQ-88219"]),
    db: Session = Depends(get_db),
):
    """
    Retrieves current status, active step, and results of a specific request from SQLite.
    Returns 404 if request does not exist.
    """
    req = repository.get_request(db, request_id=request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID '{request_id}' not found.",
        )
    return req


@router.post("", response_model=RequestItemResponse, status_code=status.HTTP_201_CREATED, summary="Create a new workflow request in SQLite")
def create_new_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
):
    """
    Persists a new workflow request in SQLite tied to a registered farmer.
    """
    # Verify farmer exists or auto-register if demo farmer
    farmer = repository.get_farmer(db, payload.farmer_id)
    if not farmer:
        # Create demo profile if needed to maintain smooth workflow
        repository.create_farmer(
            db,
            name="Demo Farmer",
            phone="9876543210",
            farmer_id=payload.farmer_id,
        )

    req = repository.create_request(
        db,
        farmer_id=payload.farmer_id,
        type=payload.type,
        status=payload.status or "pending",
        current_step=payload.current_step,
        result=payload.result,
        error_message=payload.error_message,
        request_id=payload.request_id,
    )
    return req
