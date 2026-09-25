from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from database.connection import Base


class Farmer(Base):
    """Farmer profile and identity database table."""

    __tablename__ = "farmers"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False, index=True)
    language = Column(String(16), nullable=False, default="te")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requests = relationship("Request", back_populates="farmer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="farmer", cascade="all, delete-orphan")


class Request(Base):
    """Universal agent workflow requests for a farmer."""

    __tablename__ = "requests"

    id = Column(String(64), primary_key=True, index=True)
    farmer_id = Column(String(64), ForeignKey("farmers.id"), nullable=False, index=True)
    type = Column(String(64), nullable=False)  # crop_health, tractor_booking, insurance_assistance, seed_assistance
    status = Column(String(32), nullable=False, default="pending")  # pending, awaiting_user, processing, completed, failed, cancelled
    current_step = Column(String(256), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    result = Column(Text, nullable=True)  # JSON or text result payload
    error_message = Column(Text, nullable=True)

    # Relationship
    farmer = relationship("Farmer", back_populates="requests")


class Booking(Base):
    """Tractor and farm equipment bookings."""

    __tablename__ = "bookings"

    id = Column(String(64), primary_key=True, index=True)
    farmer_id = Column(String(64), ForeignKey("farmers.id"), nullable=False, index=True)
    equipment_id = Column(String(64), nullable=False)
    equipment_name = Column(String(128), nullable=False)
    date = Column(String(32), nullable=False)
    time = Column(String(64), nullable=False)
    location = Column(String(256), nullable=False)
    price = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default="pending")  # pending, confirmed, cancelled, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    farmer = relationship("Farmer", back_populates="bookings")


class ChatMessage(Base):
    """Conversation history for multi-turn context preservation."""

    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True, index=True)
    farmer_id = Column(String(64), ForeignKey("farmers.id"), nullable=False, index=True)
    conversation_id = Column(String(64), nullable=False, index=True, default="default")
    sender = Column(String(16), nullable=False)  # "farmer" or "assistant"
    message = Column(Text, nullable=False)
    intent = Column(String(64), nullable=True)
    language = Column(String(16), nullable=False, default="te")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
