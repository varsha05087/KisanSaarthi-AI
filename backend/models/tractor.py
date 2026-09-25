from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class TractorSearchQuery(BaseModel):
    """Parameters for searching available tractors and farm equipment."""

    location: str = Field(..., description="Village, Mandal, or District location", examples=["Miryalaguda, Nalgonda"])
    date: Optional[str] = Field(None, description="Required date (YYYY-MM-DD)", examples=["2026-09-25"])
    time: Optional[str] = Field(None, description="Preferred time slot", examples=["Morning 07:00 AM"])
    equipment_type: Optional[str] = Field("tractor", description="Equipment type: tractor, harvester, rotavator, plough", examples=["tractor"])
    farmer_id: Optional[str] = Field(None, description="Requesting farmer identifier")


class TractorBookingRequest(BaseModel):
    """Parameters to confirm booking of a tractor or equipment."""

    farmer_id: str = Field(..., description="Farmer identifier", examples=["F001"])
    tractor_id: str = Field(..., description="Selected tractor or equipment identifier", examples=["TRK-575"])
    date: str = Field(..., description="Booking date (YYYY-MM-DD)", examples=["2026-09-25"])
    time: str = Field(..., description="Booking time slot", examples=["07:00 AM - 11:00 AM"])
    location: str = Field(..., description="Field delivery location", examples=["Peddapuram Village"])


class TractorCancelRequest(BaseModel):
    """Parameters to cancel an existing tractor booking."""

    farmer_id: str = Field(..., description="Farmer identifier", examples=["F001"])
    booking_id: str = Field(..., description="Booking ID to cancel", examples=["TRK-8921"])
    reason: Optional[str] = Field(None, description="Reason for cancellation", examples=["Sudden heavy rain"])


class TractorAlternativeQuery(BaseModel):
    """Parameters to search for alternative equipment when a provider cancels."""

    booking_id: Optional[str] = Field(None, description="Cancelled booking ID to replace", examples=["TRK-8921"])
    location: str = Field(..., description="Field location", examples=["Miryalaguda"])
    date: Optional[str] = Field(None, description="Required date", examples=["2026-09-25"])
    equipment_type: Optional[str] = Field("tractor", description="Equipment type needed")


class TractorResponse(BaseModel):
    """Standard response model for tractor operations."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Human-readable message")
    booking_id: Optional[str] = Field(None, description="Assigned booking identifier")
    details: Optional[Dict[str, Any]] = Field(None, description="Tractor or booking metadata")
