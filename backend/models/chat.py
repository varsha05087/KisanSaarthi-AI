from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from a farmer."""

    message: str = Field(..., min_length=1, description="Message text or voice transcript", examples=["I need a tractor tomorrow"])
    farmer_id: Optional[str] = Field("F001", description="Unique identifier of the farmer", examples=["F001"])
    language: Optional[str] = Field("te", description="Language preference: 'te', 'hi', or 'en'", examples=["te"])
    conversation_id: Optional[str] = Field(None, description="Optional ongoing conversation identifier", examples=["conv_12345"])
    sessionId: Optional[str] = Field(None, description="Frontend session identifier alias", examples=["demo-session"])


class ChatResponse(BaseModel):
    """Chat response schema."""

    status: str = Field(..., description="Execution status")
    message: str = Field(..., description="System or agent message")
    conversation_id: Optional[str] = Field(None, description="Conversation session ID")
    agent_assigned: Optional[str] = Field(None, description="Name of the agent handling the request")
