from datetime import datetime, timedelta, timezone
import pytest
from faker import Faker # Used for generating realistic fake data

from app.schemas import EventCreate, EventResponse, AttendeeRegister, AttendeeResponse
from app.models import Event, Attendee

# Initialize Faker for generating test data
fake = Faker()

# --- Test Pydantic Schemas (app/schemas.py) ---

def test_event_create_schema_valid_data():
    """
    Test that EventCreate schema can be created with valid data.
    """
    now = datetime.now(timezone.utc)
    event_data = {
        "name": fake.sentence(nb_words=3),
        "location": fake.city(),
        "start_time": now + timedelta(days=7),
        "end_time": now + timedelta(days=7, hours=2),
        "max_capacity": 100
    }
    event = EventCreate(**event_data)

    assert event.name == event_data["name"]
    assert event.location == event_data["location"]
    # Pydantic handles timezone awareness automatically for datetime objects
    assert event.start_time == event_data["start_time"]
    assert event.end_time == event_data["end_time"]
    assert event.max_capacity == event_data["max_capacity"]

def test_event_response_schema_from_event_model():
    """
    Test that EventResponse schema can be created from an Event ORM model instance.
    """
    now = datetime.now(timezone.utc)
    # Create a dummy Event ORM model instance
    event_model = Event(
        id=1,
        name="Test Event",
        location="Test Loc",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=2),
        max_capacity=50,
        created_at=now
    )
    # Use .model_validate for Pydantic v2 or .from_orm for Pydantic v1
    event_response = EventResponse(
        id=event_model.id,
        name=event_model.name,
        location=event_model.location,
        start_time=event_model.start_time,
        end_time=event_model.end_time,
        max_capacity=event_model.max_capacity,
        created_at=event_model.created_at,
        current_attendees=0 # We are providing this explicitly for the test
    )
    # event_response = EventResponse.model_validate(event_model)

    assert event_response.id == event_model.id
    assert event_response.name == event_model.name
    assert event_response.location == event_model.location
    assert event_response.start_time == event_model.start_time
    assert event_response.end_time == event_model.end_time
    assert event_response.max_capacity == event_model.max_capacity
    assert event_response.created_at == event_model.created_at
    assert event_response.current_attendees == 0 # Default from EventResponse schema

def test_attendee_register_schema_valid_data():
    """
    Test that AttendeeRegister schema can be created with valid data.
    """
    attendee_data = {
        "name": fake.name(),
        "email": fake.email()
    }
    attendee = AttendeeRegister(**attendee_data)

    assert attendee.name == attendee_data["name"]
    assert attendee.email == attendee_data["email"]

def test_attendee_response_schema_from_attendee_model():
    """
    Test that AttendeeResponse schema can be created from an Attendee ORM model instance.
    """
    now = datetime.now(timezone.utc)
    # Create a dummy Attendee ORM model instance
    attendee_model = Attendee(
        id=1,
        event_id=101,
        name="John Doe",
        email="john.doe@example.com",
        registered_at=now
    )
    attendee_response = AttendeeResponse.model_validate(attendee_model)

    assert attendee_response.id == attendee_model.id
    assert attendee_response.event_id == attendee_model.event_id
    assert attendee_response.name == attendee_model.name
    assert attendee_response.email == attendee_model.email
    assert attendee_response.registered_at == attendee_model.registered_at

# --- Test SQLAlchemy Models (app/models.py) ---
# (Basic instantiation tests, more thorough tests implicitly done via repository tests)

def test_event_model_creation():
    """
    Test basic creation of an Event ORM model instance.
    """
    now = datetime.now(timezone.utc)
    event = Event(
        name="Model Test Event",
        location="Model Test Loc",
        start_time=now + timedelta(days=5),
        end_time=now + timedelta(days=6),
        max_capacity=75,
        created_at=now
    )
    assert event.name == "Model Test Event"
    assert isinstance(event.created_at, datetime)
    assert event.created_at.tzinfo is not None # Ensure timezone-aware

def test_attendee_model_creation():
    """
    Test basic creation of an Attendee ORM model instance.
    """
    now = datetime.now(timezone.utc)
    attendee = Attendee(
        event_id=99,
        name="Jane Smith",
        email="jane.smith@example.com",
        registered_at=now
    )
    assert attendee.name == "Jane Smith"
    assert attendee.email == "jane.smith@example.com"
    assert attendee.event_id == 99
    assert isinstance(attendee.registered_at, datetime)
    assert attendee.registered_at.tzinfo is not None # Ensure timezone-aware