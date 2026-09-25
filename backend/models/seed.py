from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SeedSearchQuery(BaseModel):
    """Parameters to search seed varieties and RSK / cooperative availability."""

    farmer_id: Optional[str] = Field(None, description="Requesting farmer ID")
    crop: Optional[str] = Field(None, description="Crop name (e.g. Paddy, Cotton, Maize)", examples=["Paddy"])
    location: Optional[str] = Field(None, description="Mandal or District", examples=["Nalgonda"])
    season: Optional[str] = Field(None, description="Crop season (Kharif, Rabi)", examples=["Kharif"])


class SeedBookingRequest(BaseModel):
    """Contract for submitting a seed procurement assistance request."""

    farmer_id: str = Field(..., description="Unique farmer identifier", examples=["F001"])
    crop: str = Field(..., description="Crop name", examples=["Paddy"])
    location: str = Field(..., description="Delivery or nearby Rythu Seva Kendra (RSK) location", examples=["Chityal Mandal"])
    seed_variety: Optional[str] = Field(None, description="Preferred certified variety (e.g. BPT 5204, MTU 1010)", examples=["BPT 5204"])
    quantity: Optional[str] = Field(None, description="Requested quantity (e.g. 5 bags, 25 kg)", examples=["4 Bags (25kg)"])
    season: Optional[str] = Field(None, description="Season (e.g. Kharif)", examples=["Kharif"])
    additional_requirements: Optional[str] = Field(None, description="Requirements such as pest resistance or subsidy eligibility")


class SeedResponse(BaseModel):
    """Schema for future seed assistance recommendations."""

    status: str = Field(..., description="Assistance status")
    message: str = Field(..., description="Guidance or confirmation message")
    seed_options: List[Dict[str, Any]] = Field(default_factory=list, description="Available certified seed options and RSK centers")
    request_id: Optional[str] = Field(None, description="Assigned tracking request ID")
    request_status: Optional[str] = Field(None, description="Status of the request")
