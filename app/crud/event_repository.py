from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload

from app.models import Event, Attendee
from app.schemas import EventCreate, EventResponse

class EventRepository:
    """
    Handles database operations for Event entities.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(self, event_data: EventCreate) -> Event:
        """
        Creates a new event in the database.
        """
        # Ensure start_time and end_time are timezone-aware (UTC)
        start_time_utc = event_data.start_time.astimezone(timezone.utc)
        end_time_utc = event_data.end_time.astimezone(timezone.utc)

        db_event = Event(
            name=event_data.name,
            location=event_data.location,
            start_time=start_time_utc,
            end_time=end_time_utc,
            max_capacity=event_data.max_capacity,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(db_event)
        await self.db.commit()
        await self.db.refresh(db_event)
        return db_event

    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """
        Retrieves an event by its ID, eagerly loading attendees.
        """
        result = await self.db.execute(
            select(Event)
            .options(selectinload(Event.attendees)) # Eagerly load attendees
            .where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_all_upcoming_events(self) -> List[Event]:
        """
        Retrieves all events that have not yet ended.
        """
        current_time_utc = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Event)
            .where(Event.end_time >= current_time_utc) # Filter for upcoming events
            .order_by(Event.start_time) # Order by start time
        )
        return result.scalars().all()

    async def get_event_attendee_count(self, event_id: int) -> int:
        """
        Gets the current number of attendees for a given event.
        """
        result = await self.db.execute(
            select(func.count(Attendee.id))
            .where(Attendee.event_id == event_id)
        )
        return result.scalar_one()