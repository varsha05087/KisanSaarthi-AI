from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database import repository
from models.farmer import FarmerCreate, FarmerResponse

router = APIRouter(prefix="/api/farmers", tags=["Farmers"])


@router.post("", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED, summary="Register or create a farmer profile")
def create_farmer_profile(payload: FarmerCreate, db: Session = Depends(get_db)):
    """
    Creates a new farmer identity profile in SQLite.
    Stores farmer ID, name, phone number, and preferred language.
    """
    # Check if a farmer with this phone already exists to avoid duplicates
    existing = repository.get_farmer_by_phone(db, phone=payload.phone)
    if existing:
        return existing

    farmer = repository.create_farmer(
        db,
        name=payload.name,
        phone=payload.phone,
        language=payload.language,
        farmer_id=payload.farmer_id,
    )
    return farmer


@router.get("/{farmer_id}", response_model=FarmerResponse, summary="Retrieve farmer profile by ID")
def get_farmer_profile(farmer_id: str, db: Session = Depends(get_db)):
    """
    Retrieves farmer identity details from SQLite by farmer ID.
    Returns 404 if not found.
    """
    farmer = repository.get_farmer(db, farmer_id=farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID '{farmer_id}' not found.",
        )
    return farmer
