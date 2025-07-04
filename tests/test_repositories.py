import pytest
from datetime import datetime, timedelta, timezone
from faker import Faker
from unittest.mock import AsyncMock, MagicMock # Ensure these are imported if you need them in tests too

from app.crud.event_repository import EventRepository
from app.schemas import EventCreate
from app.models import Event, Attendee

fake = Faker()

class TestEventRepository:

    # The db_session fixture now provides an AsyncMock
    async def test_create_event(self, db_session: AsyncMock): # Type hint with AsyncMock
        """
        Test creating a new event in the repository.
        """
        repository = EventRepository(db_session)
        now = datetime.now(timezone.utc)
        event_data = EventCreate(
            name=fake.sentence(nb_words=3),
            location=fake.city(),
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=2),
            max_capacity=100
        )

        event = await repository.create_event(event_data)

        # Assertions on the mock session:
        # Check that 'add' was called with an Event instance
        db_session.add.assert_called_once()
        added_event = db_session.add.call_args[0][0]
        assert isinstance(added_event, Event)
        assert added_event.name == event_data.name
        assert added_event.location == event_data.location

        # Check that 'commit' was called
        db_session.commit.assert_called_once()
        
        # Check that 'refresh' was called with the added event
        db_session.refresh.assert_called_once_with(added_event)

        # Assertions on the returned event (its attributes should match input)
        assert event.name == event_data.name
        assert event.location == event_data.location
        assert event.max_capacity == event_data.max_capacity
        assert event.created_at is not None
        
        # You might need to set an ID on the mock event if your repository
        # relies on the ID being present immediately after creation for refresh.
        # A common pattern is to make `refresh` or `add` modify the object in place.
        # For simple mock, if your Event model has an ID, you might do:
        # if not hasattr(added_event, 'id') or added_event.id is None:
        #     added_event.id = 1 # or a mock UUID if it's a UUID field
        #     added_event.created_at = now # similar for created_at if it's auto-generated by DB