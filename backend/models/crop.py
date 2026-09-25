from typing import List, Optional, Union
from pydantic import BaseModel, Field


class CropAnalyzeRequest(BaseModel):
    """Incoming request for crop health analysis."""

    farmer_id: str = Field("F001", description="Unique farmer identifier", examples=["F001"])
    crop_name: Optional[str] = Field(None, description="Crop name if known by farmer (e.g. Tomato, Paddy, Cotton, Chilli)", examples=["Tomato"])
    image_url: Optional[str] = Field(None, description="URL or upload ID of crop photo")
    image_base64: Optional[str] = Field(None, description="Base64 encoded photo if uploaded directly")
    symptoms_description: Optional[str] = Field(None, description="Farmer's verbal or written description of symptoms", examples=["Leaves turning yellow with brown spots"])
    message: Optional[str] = Field(None, description="Farmer chat message or query")
    language: str = Field("te", description="Preferred response language", examples=["te"])
    location: Optional[str] = Field(None, description="Farmer field location or district")
    growth_stage: Optional[str] = Field(None, description="Crop stage: vegetative, flowering, fruiting, harvest")
    is_low_confidence: Optional[bool] = Field(False, description="Flag for testing/simulating low-confidence image analysis")


class CropHealthResult(BaseModel):
    """
    Structured crop health result produced by Crop Health Agent.
    Grounded in real vision analysis, ICAR knowledge base, and beginner-friendly clarity.
    """

    farmer_id: Optional[str] = Field("F001", description="Unique farmer identifier")
    crop: Optional[str] = Field(None, description="Identified crop name if recognizable")
    possible_issue: Optional[str] = Field(None, description="Possible disease, pest, or deficiency (never guaranteed)")
    possible_problem: Optional[str] = Field(None, description="Alias for possible_issue")
    confidence: Optional[float] = Field(None, description="Confidence score between 0.0 and 1.0 (internal metric)")
    uncertain: bool = Field(False, description="Whether diagnosis is uncertain or low confidence")
    
    # Visual analysis evidence
    visible_symptoms: List[str] = Field(default_factory=list, description="Direct visual leaf symptoms observed")
    evidence: List[str] = Field(default_factory=list, description="Visual features supporting the finding")
    observations: List[str] = Field(default_factory=list, description="Visual observations (backwards compatible)")

    # Curated knowledge base grounding
    knowledge_found: bool = Field(False, description="Whether curated knowledge base matched crop and problem")
    safe_next_steps: List[str] = Field(default_factory=list, description="Safe immediate non-chemical actions")
    prevention: List[str] = Field(default_factory=list, description="Long-term cultural prevention techniques")
    when_to_contact_expert: Optional[str] = Field(None, description="Specific triggers when to consult agricultural officer")
    recommendations: List[str] = Field(default_factory=list, description="Combined recommendations (backwards compatible)")
    
    # Metadata & farmer-friendly presentation
    warning: Optional[str] = Field(
        "This is an AI-assisted observation and is not a guaranteed diagnosis.",
        description="Mandatory uncertainty warning",
    )
    language: str = Field("te", description="Response language (te, hi, en)")
    status: str = Field("completed", description="Status: needs_image, invalid_image, needs_better_image, uncertain, completed")
    response: Optional[str] = Field(None, description="Farmer-friendly natural language explanation")
    next_question: Optional[str] = Field(None, description="Clarifying prompt when more details or clearer image needed")
    agent: str = Field("Crop Health Agent", description="Specialized agent name")
    request_id: Optional[str] = Field(None, description="Persisted SQLite request tracking ID")


# Backward compatibility alias
CropAnalysisResponse = CropHealthResult
