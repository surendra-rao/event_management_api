from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager # Import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db
from app.schemas import EventCreate, EventResponse, AttendeeRegister, AttendeeResponse
from app.services import EventService, EventNotFoundError, EventCapacityExceededError, \
                         DuplicateRegistrationError, InvalidEventTimeError

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the FastAPI application.
    Initializes the database tables on startup.
    """
    print("Application startup: Initializing database...")
    await init_db()
    yield # Application runs
    print("Application shutdown: Cleaning up (if any)...")
    # Here you would add any shutdown logic, e.g., closing connections


# Initialize FastAPI app with the lifespan
app = FastAPI(
    title="Mini Event Management System API",
    description="API for creating events, registering attendees, and viewing attendee lists.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan # Assign the lifespan context manager
)

# Dependency for EventService
async def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    return EventService(db)

# --- API Endpoints (rest of your main.py remains the same) ---

@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
    description="Creates a new event with specified name, location, times, and capacity."
)
async def create_event(
    event_data: EventCreate,
    event_service: EventService = Depends(get_event_service)
):
    """
    Creates a new event.

    - **name**: Name of the event.
    - **location**: Location of the event.
    - **start_time**: Start date and time of the event (ISO 8601 format, e.g., '2025-12-31T10:00:00+05:30').
    - **end_time**: End date and time of the event (ISO 8601 format, e.g., '2025-12-31T12:00:00+05:30').
    - **max_capacity**: Maximum number of attendees.
    """
    try:
        event = await event_service.create_new_event(event_data)
        return event
    except InvalidEventTimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        # For general validation errors from service layer
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get(
    "/events",
    response_model=List[EventResponse],
    summary="List all upcoming events",
    description="Retrieves a list of all events that have not yet ended, ordered by start time."
)
async def list_events(
    event_service: EventService = Depends(get_event_service)
):
    """
    Returns a list of all upcoming events.
    """
    events = await event_service.get_all_events()
    # Pydantic's from_attributes = True makes this direct conversion work
    return [EventResponse.model_validate(event) for event in events]

@app.get(
    "/events/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID (with optional timezone conversion)",
    description="Retrieves details of a specific event. Can convert event times to a specified timezone."
)
async def get_event_by_id(
    event_id: int,
    target_timezone: Optional[str] = Query(None, description="Optional target timezone (e.g., 'Asia/Kolkata'). If provided, event times will be converted."),
    event_service: EventService = Depends(get_event_service)
):
    """
    Returns details of a specific event.

    - **event_id**: The unique ID of the event.
    - **target_timezone**: Optional. Provide a valid timezone name (e.g., "Asia/Kolkata") to convert event start and end times to that timezone in the response.
    """
    try:
        event = await event_service.get_event(event_id)

        if target_timezone:
            return await event_service.convert_event_timezone(event, target_timezone)
        
        return EventResponse.model_validate(event)
    except EventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post(
    "/events/{event_id}/register",
    response_model=AttendeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register an attendee for an event",
    description="Registers a new attendee for a specific event, preventing overbooking and duplicate registrations."
)
async def register_attendee(
    event_id: int,
    attendee_data: AttendeeRegister,
    event_service: EventService = Depends(get_event_service)
):
    """
    Registers an attendee for a given event.

    - **event_id**: The unique ID of the event.
    - **name**: Name of the attendee.
    - **email**: Email address of the attendee.

    **Business Rules Applied:**
    - Prevents overbooking (checks `max_capacity`).
    - Prevents duplicate registrations (same email for same event).
    - Prevents registration for events that have already ended.
    """
    try:
        attendee = await event_service.register_attendee_for_event(event_id, attendee_data)
        return attendee
    except EventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EventCapacityExceededError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DuplicateRegistrationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidEventTimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get(
    "/events/{event_id}/attendees",
    response_model=List[AttendeeResponse],
    summary="List registered attendees for an event",
    description="Returns all registered attendees for a specific event, with pagination."
)
async def list_attendees_for_event(
    event_id: int,
    skip: int = Query(0, ge=0, description="Number of attendees to skip (for pagination)"),
    limit: int = Query(100, gt=0, le=200, description="Maximum number of attendees to return (for pagination)"),
    event_service: EventService = Depends(get_event_service)
):
    """
    Returns a list of all registered attendees for a specific event.

    - **event_id**: The unique ID of the event.
    - **skip**: Number of records to skip for pagination.
    - **limit**: Maximum number of records to return.
    """
    try:
        attendees = await event_service.get_attendees_for_event(event_id, skip, limit)
        return [AttendeeResponse.model_validate(attendee) for attendee in attendees]
    except EventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))