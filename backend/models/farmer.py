from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FarmerCreate(BaseModel):
    """Schema for creating a demo farmer profile."""

    name: str = Field(..., min_length=1, description="Farmer's full name", examples=["Ramu"])
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number as a string", examples=["9876543210"])
    language: str = Field("te", description="Preferred language code ('te', 'hi', 'en')", examples=["te"])
    farmer_id: Optional[str] = Field(None, description="Optional custom farmer identifier")


class FarmerResponse(BaseModel):
    """Schema for returning farmer profile details."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique farmer ID")
    name: str = Field(..., description="Farmer's name")
    phone: str = Field(..., description="Farmer's phone number")
    language: str = Field(..., description="Preferred language")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
