import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from database.models import Booking, ChatMessage, Farmer, Request


# ==========================================
# FARMER REPOSITORY FUNCTIONS
# ==========================================

def create_farmer(
    db: Session,
    name: str,
    phone: str,
    language: str = "te",
    farmer_id: Optional[str] = None,
) -> Farmer:
    """Creates a new farmer profile in SQLite."""
    if not farmer_id:
        farmer_id = f"FARMER-{uuid.uuid4().hex[:8].upper()}"

    db_farmer = Farmer(
        id=farmer_id,
        name=name,
        phone=str(phone),
        language=language,
    )
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, farmer_id: str) -> Optional[Farmer]:
    """Retrieves a farmer by their unique ID."""
    return db.query(Farmer).filter(Farmer.id == farmer_id).first()


def get_farmer_by_phone(db: Session, phone: str) -> Optional[Farmer]:
    """Retrieves a farmer by their phone number."""
    return db.query(Farmer).filter(Farmer.phone == str(phone)).first()


# ==========================================
# REQUEST REPOSITORY FUNCTIONS
# ==========================================

def create_request(
    db: Session,
    farmer_id: str,
    type: str,
    status: str = "pending",
    current_step: Optional[str] = None,
    result: Optional[str] = None,
    error_message: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Request:
    """Creates a new workflow request tied to a farmer."""
    if not request_id:
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

    db_request = Request(
        id=request_id,
        farmer_id=farmer_id,
        type=type,
        status=status,
        current_step=current_step,
        result=result,
        error_message=error_message,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_request(db: Session, request_id: str) -> Optional[Request]:
    """Retrieves a single request by ID."""
    return db.query(Request).filter(Request.id == request_id).first()


def list_farmer_requests(db: Session, farmer_id: Optional[str] = None) -> List[Request]:
    """Lists requests, optionally filtered by farmer_id, sorted latest first."""
    query = db.query(Request)
    if farmer_id:
        query = query.filter(Request.farmer_id == farmer_id)
    return query.order_by(Request.created_at.desc()).all()


def update_request(
    db: Session,
    request_id: str,
    status: Optional[str] = None,
    current_step: Optional[str] = None,
    result: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Optional[Request]:
    """Updates status or result of an existing request."""
    db_request = get_request(db, request_id)
    if not db_request:
        return None

    if status is not None:
        db_request.status = status
    if current_step is not None:
        db_request.current_step = current_step
    if result is not None:
        db_request.result = result
    if error_message is not None:
        db_request.error_message = error_message

    db.commit()
    db.refresh(db_request)
    return db_request


# ==========================================
# BOOKING REPOSITORY FUNCTIONS
# ==========================================

def create_booking(
    db: Session,
    farmer_id: str,
    equipment_id: str,
    equipment_name: str,
    date: str,
    time: str,
    location: str,
    price: Optional[float] = None,
    status: str = "confirmed",
    booking_id: Optional[str] = None,
) -> Booking:
    """Creates a persistent tractor or implement booking."""
    if not booking_id:
        booking_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"

    db_booking = Booking(
        id=booking_id,
        farmer_id=farmer_id,
        equipment_id=equipment_id,
        equipment_name=equipment_name,
        date=date,
        time=time,
        location=location,
        price=price,
        status=status,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_booking(db: Session, booking_id: str) -> Optional[Booking]:
    """Retrieves a booking by ID."""
    return db.query(Booking).filter(Booking.id == booking_id).first()


def list_farmer_bookings(db: Session, farmer_id: Optional[str] = None) -> List[Booking]:
    """Lists bookings, optionally filtered by farmer_id, sorted latest first."""
    query = db.query(Booking)
    if farmer_id:
        query = query.filter(Booking.farmer_id == farmer_id)
    return query.order_by(Booking.created_at.desc()).all()


def update_booking_status(db: Session, booking_id: str, status: str) -> Optional[Booking]:
    """Updates booking status (e.g. cancelled, confirmed)."""
    booking = get_booking(db, booking_id)
    if not booking:
        return None
    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking


# ==========================================
# CHAT CONVERSATION REPOSITORY FUNCTIONS
# ==========================================

def save_chat_message(
    db: Session,
    farmer_id: str,
    sender: str,
    message: str,
    conversation_id: str = "default",
    intent: Optional[str] = None,
    language: str = "te",
) -> ChatMessage:
    """Saves a conversation message in SQLite for contextual multi-turn tracking."""
    msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    db_msg = ChatMessage(
        id=msg_id,
        farmer_id=farmer_id,
        conversation_id=conversation_id,
        sender=sender,
        message=message,
        intent=intent,
        language=language,
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


def get_conversation_history(
    db: Session,
    farmer_id: str,
    conversation_id: str = "default",
    limit: int = 10,
) -> List[ChatMessage]:
    """Retrieves recent conversation messages for contextual continuity."""
    recent_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.farmer_id == farmer_id, ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(recent_msgs))

