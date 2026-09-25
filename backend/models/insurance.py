from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InsuranceAssistanceRequest(BaseModel):
    """
    Contract for farmer insurance assistance requests.
    Supports claim preparation, document gathering, and incident recording.
    """

    farmer_id: str = Field(..., description="Unique farmer identifier", examples=["F001"])
    language: str = Field("te", description="Language preference for notifications & draft", examples=["te"])
    request_type: str = Field(
        "claim_preparation",
        description="Assistance category: 'claim_preparation', 'loss_assessment', or 'scheme_inquiry'",
        examples=["claim_preparation"],
    )
    crop: str = Field(..., description="Affected insured crop", examples=["Paddy"])
    location: str = Field(..., description="Survey number, village, or mandal", examples=["Sy. No. 142, Suryapet"])
    policy_number: Optional[str] = Field(None, description="PMFBY policy or application number if known", examples=["PMFBY-2026-88192"])
    incident_date: Optional[str] = Field(None, description="Date of damage/loss event (YYYY-MM-DD)", examples=["2026-09-20"])
    incident_description: Optional[str] = Field(None, description="Details of loss event (e.g. unseasonal rain, hailstorm, pest attack)", examples=["Severe waterlogging due to heavy rains"])
    documents_available: List[str] = Field(
        default_factory=list,
        description="Documents the farmer currently possesses",
        examples=[["Pattadar Passbook", "Aadhaar Card"]],
    )
    documents_missing: List[str] = Field(
        default_factory=list,
        description="Documents the farmer still requires or is unsure about",
        examples=[["Crop Sowing Certificate", "Geo-tagged photo"]],
    )
    additional_notes: Optional[str] = Field(None, description="Any additional context provided by the farmer")


class InsuranceChecklistQuery(BaseModel):
    """Parameters for querying required claim documents and deadlines."""

    crop: str = Field(..., description="Insured crop name", examples=["Paddy"])
    scheme: Optional[str] = Field("PMFBY", description="Insurance scheme (default: PMFBY)", examples=["PMFBY"])
    season: Optional[str] = Field(None, description="Season (e.g. Kharif, Rabi)")


class InsuranceAssistanceResponse(BaseModel):
    """
    Schema for future Insurance Agent responses.
    Clear guidance model with disclaimers.
    """

    status: str = Field(..., description="Assistance status (e.g. draft_prepared, guidance_provided)")
    message: str = Field(..., description="Summary message for farmer in their language")
    assistance_type: Optional[str] = Field(None, description="Category of assistance provided")
    required_documents: List[str] = Field(default_factory=list, description="Mandatory documents list")
    missing_documents: List[str] = Field(default_factory=list, description="Documents remaining to be gathered")
    next_steps: List[str] = Field(default_factory=list, description="Actionable step-by-step guidance")
    warnings: List[str] = Field(default_factory=list, description="Important deadlines or official portal disclaimers")
    request_status: Optional[str] = Field(None, description="Workflow tracking status")


class InsuranceAssistPayload(BaseModel):
    farmer_id: Optional[str] = Field("FARMER-DEFAULT", description="Unique farmer identifier")
    message: str = Field(..., description="Farmer message or query describing crop damage / insurance need")
    language: Optional[str] = Field("en", description="Language preference ('en', 'te', 'hi')")
    request_id: Optional[str] = Field(None, description="Existing request ID if continuing conversation")


class InsuranceAssistResponse(BaseModel):
    request_id: str = Field(..., description="Unique persistent request ID")
    intent: str = Field("insurance_assistance", description="Detected intent")
    status: str = Field(..., description="Status: 'information_collection', 'report_generated', or 'ready'")
    message: str = Field(..., description="Agent's localized response or question")
    missing_information: List[str] = Field(default_factory=list, description="Fields still needed for report")
    collected_information: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters so far")
    retrieved_topic: Optional[str] = Field(None, description="Matched peril or insurance topic ID")
    report: Optional[str] = Field(None, description="Generated preliminary incident report if completed")
