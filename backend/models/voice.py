from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class VoiceRequest(BaseModel):
    """Voice interaction payload contract."""

    farmer_id: str = Field(..., description="Unique identifier of the farmer", examples=["F001"])
    language: str = Field("te", description="Spoken language code (e.g. te, hi, en)", examples=["te"])
    audio_format: Optional[str] = Field("webm", description="Format/container of the audio (e.g. webm, wav, mp3)")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded audio payload if passed inline")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz (e.g. 16000, 44100)")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Device and audio recording metadata")


class VoiceResponse(BaseModel):
    """Voice interaction response contract."""

    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status description")
    transcription: Optional[str] = Field(None, description="Transcribed text from speech")
    confidence: Optional[float] = Field(None, description="Transcription confidence score")
    audio_response_url: Optional[str] = Field(None, description="URL or data of synthesized speech response")
