"""
Crop Health API Router for KisanSaarthi AI.
Provides endpoints for visual crop diagnosis, disease detection, and agronomic guidance.
"""

import base64
from typing import Optional
from fastapi import APIRouter, Depends, Request, UploadFile
from sqlalchemy.orm import Session

from database.connection import get_db
from models.crop import CropAnalyzeRequest, CropHealthResult
from agents.crop_health_agent import CropHealthAgent

router = APIRouter(prefix="/api/crop", tags=["Crop Health"])


@router.post(
    "/health",
    response_model=CropHealthResult,
    summary="Analyze crop health with optional image upload",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "image": {
                                "type": "string",
                                "format": "binary",
                                "description": "Optional clear photo of the affected crop leaf/stem",
                            },
                            "farmer_id": {"type": "string", "default": "F001"},
                            "crop_name": {"type": "string", "description": "Optional crop name (Tomato, Cotton, Rice, Chilli)"},
                            "location": {"type": "string", "description": "Farmer field location or district"},
                            "growth_stage": {"type": "string", "description": "Crop stage: vegetative, flowering, fruiting"},
                            "message": {"type": "string", "default": "ఆకులపై మచ్చలు కనిపిస్తున్నాయి"},
                            "language": {"type": "string", "default": "te"},
                            "is_low_confidence": {"type": "boolean", "default": False},
                        },
                    }
                },
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/CropAnalyzeRequest"}
                },
            }
        }
    },
)
async def crop_health(request: Request, db: Session = Depends(get_db)):
    """
    Thin API endpoint connecting a farmer's crop-health request and optional image
    to the Crop Health Agent and Vision Service.

    Flow: Request/Image -> CropHealthAgent -> VisionService -> KnowledgeBase -> CropHealthResult
    """
    content_type = request.headers.get("content-type", "")
    farmer_id = "F001"
    message = ""
    language = "te"
    crop_name = None
    location = None
    growth_stage = None
    is_low_confidence = False
    image_bytes: Optional[bytes] = None
    filename: Optional[str] = None

    if "application/json" in content_type:
        body = await request.json()
        farmer_id = body.get("farmer_id") or "F001"
        message = body.get("message") or body.get("symptoms_description") or ""
        language = body.get("language") or "te"
        crop_name = body.get("crop_name")
        location = body.get("location")
        growth_stage = body.get("growth_stage")
        is_low_confidence = bool(body.get("is_low_confidence", False))
        if body.get("image_base64"):
            try:
                image_bytes = base64.b64decode(body["image_base64"])
                filename = body.get("filename") or "upload.jpg"
            except Exception:
                image_bytes = b"corrupted"
        elif body.get("image_bytes"):
            image_bytes = body["image_bytes"].encode("latin1")
            filename = body.get("filename") or "upload.jpg"
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        farmer_id = form.get("farmer_id") or "F001"
        message = form.get("message") or ""
        language = form.get("language") or "te"
        crop_name = form.get("crop_name")
        location = form.get("location")
        growth_stage = form.get("growth_stage")
        is_low_confidence = form.get("is_low_confidence") in [True, "true", "True", "1"]
        upload_item = form.get("image") or form.get("file")
        if upload_item and hasattr(upload_item, "read"):
            filename = getattr(upload_item, "filename", "upload.jpg")
            image_bytes = await upload_item.read()
    else:
        # Default empty fallback
        pass

    return CropHealthAgent.process_request(
        farmer_id=farmer_id,
        message=message,
        language=language,
        image_bytes=image_bytes,
        filename=filename,
        crop_name=crop_name,
        location=location,
        growth_stage=growth_stage,
        is_low_confidence=is_low_confidence,
        db=db,
    )


@router.post("/analyze", response_model=CropHealthResult, summary="Analyze crop health from JSON request")
async def analyze_crop(payload: CropAnalyzeRequest, db: Session = Depends(get_db)):
    """
    JSON API endpoint for crop health analysis, reusing the CropHealthAgent pipeline.
    """
    image_bytes = None
    filename = None
    if payload.image_base64:
        try:
            image_bytes = base64.b64decode(payload.image_base64)
            filename = payload.crop_name or "crop_image.jpg"
        except Exception:
            image_bytes = b"corrupted"

    return CropHealthAgent.process_request(
        farmer_id=payload.farmer_id or "F001",
        message=payload.message or payload.symptoms_description or "",
        language=payload.language or "te",
        image_bytes=image_bytes,
        filename=filename,
        crop_name=payload.crop_name,
        location=payload.location,
        growth_stage=payload.growth_stage,
        is_low_confidence=bool(payload.is_low_confidence),
        db=db,
    )
