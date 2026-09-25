from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database import repository
from models.tractor import TractorBookingRequest, TractorCancelRequest, TractorResponse
from models.request import NotImplementedResponse

router = APIRouter(prefix="/api/tractors", tags=["Tractors & Equipment"])


@router.get("", response_model=NotImplementedResponse, summary="Search available tractors and equipment")
async def list_tractors(
    location: str = Query(..., description="Village / Mandal / District location"),
    equipment_type: Optional[str] = Query("tractor", description="Equipment type: tractor, harvester, plough"),
    date: Optional[str] = Query(None, description="Booking date needed (YYYY-MM-DD)"),
    farmer_id: Optional[str] = Query(None, description="Farmer identifier"),
):
    """
    Searches nearby available tractors and equipment.
    (Inventory tools/agent workflow will be connected in a later step.)
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/tractors",
    )


@router.post("/book", response_model=TractorResponse, summary="Book a tractor or farm equipment")
def book_tractor(payload: TractorBookingRequest, db: Session = Depends(get_db)):
    """
    Submits and persists a tractor/equipment booking into SQLite.
    Also records an associated workflow request.
    """
    # Ensure farmer exists in DB
    farmer = repository.get_farmer(db, payload.farmer_id)
    if not farmer:
        repository.create_farmer(
            db,
            name="Demo Farmer",
            phone="9876543210",
            farmer_id=payload.farmer_id,
        )

    # Persist booking in SQLite
    booking = repository.create_booking(
        db,
        farmer_id=payload.farmer_id,
        equipment_id=payload.tractor_id,
        equipment_name="Mahindra 575 DI (45 HP)",
        date=payload.date,
        time=payload.time,
        location=payload.location,
        price=850.0,
        status="confirmed",
    )

    # Also persist corresponding request record
    repository.create_request(
        db,
        farmer_id=payload.farmer_id,
        type="tractor_booking",
        status="completed",
        current_step="Booking confirmed with provider",
        result=f"Tractor {payload.tractor_id} booked for {payload.date} {payload.time}",
    )

    return TractorResponse(
        status="confirmed",
        message="Tractor booking successfully stored in database.",
        booking_id=booking.id,
        details={
            "equipment_id": booking.equipment_id,
            "equipment_name": booking.equipment_name,
            "date": booking.date,
            "time": booking.time,
            "location": booking.location,
            "price": booking.price,
            "status": booking.status,
        },
    )


@router.post("/cancel", response_model=TractorResponse, summary="Cancel an existing tractor booking")
def cancel_tractor(payload: TractorCancelRequest, db: Session = Depends(get_db)):
    """
    Cancels an existing booking in SQLite.
    """
    updated = repository.update_booking_status(db, payload.booking_id, status="cancelled")
    return TractorResponse(
        status="cancelled" if updated else "not_found",
        message="Booking cancelled in database." if updated else f"Booking '{payload.booking_id}' not found.",
        booking_id=payload.booking_id,
    )


@router.get("/alternatives", response_model=NotImplementedResponse, summary="Search for replacement equipment")
async def get_alternatives(
    location: str = Query(..., description="Field location"),
    booking_id: Optional[str] = Query(None, description="Previous cancelled booking ID"),
    equipment_type: Optional[str] = Query("tractor", description="Equipment type needed"),
):
    """
    Dispatches the Tractor Agent recovery workflow to locate alternative equipment.
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/tractors/alternatives",
    )
