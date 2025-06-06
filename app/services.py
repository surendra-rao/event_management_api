from typing import List, Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Attendee
from app.schemas import EventCreate, AttendeeRegister, EventResponse, AttendeeResponse
from app.crud.event_repository import EventRepository
from app.crud.attendee_repository import AttendeeRepository

# Custom Exceptions for Business Logic
class EventNotFoundError(Exception):
    """Raised when an event with the given ID is not found."""
    def __init__(self, detail: str = "Event not found"):
        self.detail = detail
        super().__init__(self.detail)

class EventCapacityExceededError(Exception):
    """Raised when event capacity is exceeded."""
    def __init__(self, detail: str = "Event capacity exceeded"):
        self.detail = detail
        super().__init__(self.detail)

class DuplicateRegistrationError(Exception):
    """Raised when an attendee tries to register multiple times for the same event."""
    def __init__(self, detail: str = "Attendee already registered for this event with this email"):
        self.detail = detail
        super().__init__(self.detail)

class InvalidEventTimeError(Exception):
    """Raised when event start time is after end time, or in the past."""
    def __init__(self, detail: str = "Event start time cannot be in the past or after the end time"):
        self.detail = detail
        super().__init__(self.detail)

class EventService:
    """
    Handles business logic related to Event management.
    """
    def __init__(self, db: AsyncSession):
        self.event_repo = EventRepository(db)
        self.attendee_repo = AttendeeRepository(db) # We need attendee repo for capacity checks

    async def create_new_event(self, event_data: EventCreate) -> Event:
        """
        Creates a new event, applying business rules.
        """
        # Business Rule: Event start time cannot be in the past
        current_time_utc = datetime.now(timezone.utc)
        if event_data.start_time.astimezone(timezone.utc) < current_time_utc:
            raise InvalidEventTimeError("Event start time cannot be in the past.")

        # Business Rule: Event start time must be before end time
        if event_data.start_time >= event_data.end_time:
            raise InvalidEventTimeError("Event start time must be before end time.")

        # Business Rule: Max capacity must be positive
        if event_data.max_capacity <= 0:
            raise ValueError("Max capacity must be a positive number.")

        return await self.event_repo.create_event(event_data)

    async def get_event(self, event_id: int) -> Event:
        """
        Retrieves a single event by ID.
        """
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID {event_id} not found.")
        return event

    async def get_all_events(self) -> List[Event]:
        """
        Retrieves all upcoming events.
        """
        return await self.event_repo.get_all_upcoming_events()

    async def register_attendee_for_event(self, event_id: int, attendee_data: AttendeeRegister) -> Attendee:
        """
        Registers an attendee for an event, enforcing capacity and duplicate checks.
        """
        event = await self.get_event(event_id) # Reuse get_event to check existence

        # Business Rule: Prevent duplicate registrations
        existing_attendee = await self.attendee_repo.get_attendee_by_email_and_event(event_id, attendee_data.email)
        if existing_attendee:
            raise DuplicateRegistrationError("Attendee with this email is already registered for this event.")

        # Business Rule: Prevent overbooking
        current_attendee_count = await self.event_repo.get_event_attendee_count(event_id)
        if current_attendee_count >= event.max_capacity:
            raise EventCapacityExceededError(f"Event '{event.name}' (ID: {event_id}) has reached its maximum capacity of {event.max_capacity}.")

        # Business Rule: Cannot register for an event that has already ended
        current_time_utc = datetime.now(timezone.utc)
        if event.end_time.astimezone(timezone.utc) < current_time_utc:
            raise InvalidEventTimeError("Cannot register for an event that has already ended.")

        return await self.attendee_repo.create_attendee(event_id, attendee_data)

    async def get_attendees_for_event(self, event_id: int, skip: int = 0, limit: int = 100) -> List[Attendee]:
        """
        Retrieves attendees for a specific event with pagination.
        """
        event = await self.get_event(event_id) # Check if event exists before fetching attendees
        return await self.attendee_repo.get_attendees_for_event(event_id, skip, limit)

    async def convert_event_timezone(self, event: Event, target_timezone_name: str) -> EventResponse:
        """
        Converts an event's start and end times to a specified timezone.
        Returns an EventResponse schema with converted times.
        """
        try:
            # We need to import pytz for timezone conversion
            import pytz
            target_tz = pytz.timezone(target_timezone_name)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {target_timezone_name}")

        # Convert UTC times from DB to target timezone
        event.start_time = event.start_time.astimezone(target_tz)
        event.end_time = event.end_time.astimezone(target_tz)

        # We return an EventResponse schema which includes all event details
        # and has `from_attributes = True` which will handle conversion from ORM model
        return EventResponse.model_validate(event) # Pydantic v2+ method