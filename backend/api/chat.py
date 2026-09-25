from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from models.chat import ChatRequest
from models.orchestrator import OrchestratorResponse
from services.orchestrator import KisanSaarthiOrchestrator

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=OrchestratorResponse, summary="Send message to KisanSaarthi Orchestrator")
def chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Thin API endpoint connecting the farmer's chat message to the KisanSaarthi LangGraph Orchestrator.
    Flow: Request -> KisanSaarthiOrchestrator -> Compiled LangGraph Workflow -> Agent Node -> Post Processor -> OrchestratorResponse
    """
    return KisanSaarthiOrchestrator.process(
        farmer_id=payload.farmer_id or "F001",
        message=payload.message,
        language=payload.language or "te",
        conversation_id=payload.conversation_id or payload.sessionId or "default",
        db=db,
    )
