from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models import Attendee
from app.schemas import AttendeeRegister

class AttendeeRepository:
    """
    Handles database operations for Attendee entities.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_attendee(self, event_id: int, attendee_data: AttendeeRegister) -> Attendee:
        """
        Registers a new attendee for a specific event.
        """
        db_attendee = Attendee(
            event_id=event_id,
            name=attendee_data.name,
            email=attendee_data.email,
            registered_at=datetime.now(timezone.utc)
        )
        self.db.add(db_attendee)
        await self.db.commit()
        await self.db.refresh(db_attendee)
        return db_attendee

    async def get_attendee_by_email_and_event(self, event_id: int, email: str) -> Optional[Attendee]:
        """
        Checks if an attendee with the given email is already registered for an event.
        """
        result = await self.db.execute(
            select(Attendee)
            .where(and_(Attendee.event_id == event_id, Attendee.email == email))
        )
        return result.scalar_one_or_none()

    async def get_attendees_for_event(self, event_id: int, skip: int = 0, limit: int = 100) -> List[Attendee]:
        """
        Retrieves all registered attendees for a specific event with pagination.
        """
        result = await self.db.execute(
            select(Attendee)
            .where(Attendee.event_id == event_id)
            .offset(skip)
            .limit(limit)
            .order_by(Attendee.registered_at) # Order by registration time
        )
        return result.scalars().all()