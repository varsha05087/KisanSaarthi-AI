from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class RequestType(str, Enum):
    """Supported agentic workflow request types."""

    crop_health = "crop_health"
    tractor_booking = "tractor_booking"
    insurance_assistance = "insurance_assistance"
    seed_assistance = "seed_assistance"


class RequestStatus(str, Enum):
    """Workflow execution states."""

    pending = "pending"
    awaiting_user = "awaiting_user"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class RequestCreate(BaseModel):
    """Schema for creating a workflow request in SQLite."""

    farmer_id: str = Field(..., description="Farmer identifier", examples=["F001"])
    type: str = Field(
        ...,
        description="Workflow type: crop_health, tractor_booking, insurance_assistance, seed_assistance",
        examples=["tractor_booking"],
    )
    status: Optional[str] = Field("pending", description="Initial status")
    current_step: Optional[str] = Field("Request submitted", description="Initial step description")
    result: Optional[str] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None


class RequestItemResponse(BaseModel):
    """Schema for returning a persistent workflow request from SQLite."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    farmer_id: str
    type: str
    status: str
    current_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    result: Optional[str] = None
    error_message: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Universal schema representing a farmer's workflow request in KisanSaarthi."""

    request_id: str = Field(..., description="Unique workflow identifier", examples=["REQ-88219"])
    farmer_id: str = Field(..., description="Farmer identifier who created this request", examples=["F001"])
    type: RequestType = Field(..., description="Type of agricultural workflow", examples=[RequestType.tractor_booking])
    status: RequestStatus = Field(default=RequestStatus.pending, description="Current workflow state", examples=[RequestStatus.pending])
    current_step: Optional[str] = Field(None, description="Human-readable description of current agent step", examples=["Checking nearest available tractors"])
    created_at: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Result payload if completed")
    error: Optional[str] = Field(None, description="Error message if workflow failed")


class NotImplementedResponse(BaseModel):
    """Standard development response for endpoints awaiting agent implementation."""

    status: str = Field("not_implemented", description="Status code indicating contract-only state")
    message: str = Field(
        "This workflow will be connected to the appropriate agent in a later phase.",
        description="Development notice",
    )
    endpoint: Optional[str] = Field(None, description="Invoked endpoint name")
