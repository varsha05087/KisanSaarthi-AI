from fastapi import APIRouter
from models.voice import VoiceRequest
from models.request import NotImplementedResponse

router = APIRouter(prefix="/api/voice", tags=["Voice"])


@router.post("", response_model=NotImplementedResponse, summary="Process spoken voice interaction")
async def voice_interaction(payload: VoiceRequest):
    """
    Accepts voice metadata or encoded audio payload for STT/Agent pipeline.
    Validates payload structure and returns placeholder contract response.
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/voice",
    )
