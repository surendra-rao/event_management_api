from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# --- Base Schemas (for shared attributes or common fields) ---

class EventBase(BaseModel):
    """Base schema for Event, including common attributes."""
    name: str = Field(..., max_length=255, description="Name of the event")
    location: str = Field(..., max_length=255, description="Location where the event will take place")
    start_time: datetime = Field(..., description="Start time of the event (UTC recommended)")
    end_time: datetime = Field(..., description="End time of the event (UTC recommended)")
    max_capacity: int = Field(..., ge=1, description="Maximum number of attendees allowed for the event")

    class Config:
        """Pydantic configuration for ORM mode."""
        from_attributes = True # This replaces `orm_mode = True` in Pydantic v2+

class AttendeeBase(BaseModel):
    """Base schema for Attendee, including common attributes."""
    name: str = Field(..., max_length=255, description="Name of the attendee")
    email: EmailStr = Field(..., max_length=320, description="Email address of the attendee")

    class Config:
        from_attributes = True # Allows Pydantic to read ORM models directly

# --- Create/Input Schemas (for POST requests) ---

class EventCreate(EventBase):
    """Schema for creating a new Event."""
    # Inherits all fields from EventBase. No extra fields needed for creation.
    pass

class AttendeeRegister(AttendeeBase):
    """Schema for registering an Attendee for an event."""
    # Inherits all fields from AttendeeBase. No extra fields needed for registration.
    pass

# --- Response Schemas (for GET requests - what the API returns) ---

class AttendeeResponse(AttendeeBase):
    """Schema for returning Attendee data, including ID and timestamp."""
    id: int = Field(..., description="Unique ID of the attendee")
    event_id: int = Field(..., description="ID of the event the attendee is registered for")
    registered_at: datetime = Field(..., description="Timestamp of when the attendee registered (UTC)")

class EventResponse(EventBase):
    """Schema for returning Event data, including ID, timestamp, and attendees."""
    id: int = Field(..., description="Unique ID of the event")
    created_at: datetime = Field(..., description="Timestamp of when the event was created (UTC)")
    current_attendees: int = Field(0, description="Current number of attendees registered for the event")
    # Optional: If you want to embed attendees directly in the event response.
    # We will initially exclude this to keep responses lean, but you can uncomment later.
    # attendees: List[AttendeeResponse] = []