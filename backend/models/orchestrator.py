from typing import List, Optional
from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """Sub-task created by the orchestrator for a specialized agent."""

    intent: str = Field(..., description="Target intent for this task", examples=["tractor_booking"])
    agent: str = Field(..., description="Assigned agent name", examples=["Tractor Booking Agent"])
    description: str = Field(..., description="Task summary", examples=["Book tractor for tomorrow"])
    request_id: Optional[str] = Field(None, description="Persistent tracking ID in SQLite")


class OrchestratorResponse(BaseModel):
    """Structured response from the KisanSaarthi Orchestrator."""

    farmer_id: str = Field(..., description="Farmer identifier", examples=["F001"])
    message: str = Field(..., description="Original input message received", examples=["I need a tractor tomorrow"])
    language: str = Field("te", description="Language preference ('te', 'hi', 'en')", examples=["en"])
    intent: str = Field(
        ...,
        description="Identified intent: crop_health, tractor_booking, insurance_assistance, seed_assistance, general_help, unknown, or multi_intent",
        examples=["tractor_booking"],
    )
    status: str = Field(
        ...,
        description="Orchestrator status: 'ready', 'needs_information', 'needs_clarification', or 'multi_task'",
        examples=["ready"],
    )
    agent: Optional[str] = Field(None, description="Primary specialized agent assigned", examples=["Tractor Booking Agent"])
    missing_information: List[str] = Field(default_factory=list, description="Missing data points required by the agent")
    next_question: Optional[str] = Field(None, description="Single conversational follow-up question")
    tasks: List[AgentTask] = Field(default_factory=list, description="List of recognized tasks (supports multi-intent)")
    response: str = Field(..., description="Conversational explanation or guidance for the farmer")
    text: Optional[str] = Field(None, description="Direct text response for chat UI compatibility")
    id: Optional[str] = Field(None, description="Message identifier")
    sender: str = Field("agent", description="Message sender identity")
    timestamp: Optional[str] = Field(None, description="Formatted response timestamp")
    options: Optional[List[dict]] = Field(default=None, description="Available equipment options")
    confirmation_details: Optional[dict] = Field(default=None, description="Booking and farmer details awaiting confirmation")
    booking: Optional[dict] = Field(default=None, description="Confirmed booking summary")
