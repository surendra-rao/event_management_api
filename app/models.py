import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Event(Base):
    """
    Represents an event in the database.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), index=True, nullable=False)
    location = Column(String(520), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False) # Store timezone-aware datetime
    end_time = Column(DateTime(timezone=True), nullable=False)   # Store timezone-aware datetime
    max_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))

    # Relationship to attendees
    attendees = relationship("Attendee", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}')>"

class Attendee(Base):
    """
    Represents an attendee registered for an event in the database.
    """
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(320), index=True, nullable=False) # Add index for faster lookup, esp. for duplicates
    registered_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))

    # Relationship to event
    event = relationship("Event", back_populates="attendees")

    def __repr__(self):
        return f"<Attendee(id={self.id}, name='{self.name}', event_id={self.event_id})>"