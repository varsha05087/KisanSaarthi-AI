from typing import Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.insurance import InsuranceAssistPayload, InsuranceAssistResponse
from agents.insurance import InsuranceAgent
from models.request import NotImplementedResponse

router = APIRouter(prefix="/api/insurance", tags=["Crop Insurance"])


@router.post("/assist", response_model=InsuranceAssistResponse, summary="Submit insurance claim assistance request")
async def insurance_assistance(payload: InsuranceAssistPayload, db: Session = Depends(get_db)):
    """
    Processes farmer crop damage or insurance inquiries.
    Supports multi-turn information collection and generates preliminary incident reports.
    """
    farmer_id = payload.farmer_id or "FARMER-DEFAULT"
    result = InsuranceAgent.execute(
        farmer_id=farmer_id,
        query=payload.message,
        language=payload.language or "en",
        db=db,
        request_id=payload.request_id,
    )
    return InsuranceAssistResponse(
        request_id=result.get("request_id", "REQ-INS-000"),
        intent="insurance_assistance",
        status=result.get("status", "information_collection"),
        message=result.get("message") or result.get("response", ""),
        missing_information=result.get("missing_information", []),
        collected_information=result.get("collected_information", {}),
        retrieved_topic=result.get("retrieved_topic"),
        report=result.get("report"),
    )


@router.get("/checklist", response_model=NotImplementedResponse, summary="Query required claim documentation")
async def insurance_checklist(
    crop: str = Query(..., description="Insured crop name (e.g. Paddy, Cotton)"),
    scheme: Optional[str] = Query("PMFBY", description="Crop insurance scheme (default: PMFBY)"),
    season: Optional[str] = Query(None, description="Season (e.g. Kharif, Rabi)"),
):
    """
    Retrieves required documentation checklist and deadlines for crop insurance claims.
    Validates query parameters and returns placeholder contract response.
    """
    return NotImplementedResponse(
        status="not_implemented",
        message="This workflow will be connected to the appropriate agent in a later phase.",
        endpoint="/api/insurance/checklist",
    )
