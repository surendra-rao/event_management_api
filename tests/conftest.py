import pytest
import asyncio
from typing import AsyncGenerator
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # No longer needed
# from sqlalchemy.orm import sessionmaker # No longer needed

import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock # Import AsyncMock and MagicMock

# from app.models import Base # No longer directly used by db_session fixture
from main import app # Import your FastAPI app
from database import get_db # Import get_db from your database.py, needed for client fixture
import httpx # Import httpx for the test client

# 1. IMPORTANT: Explicitly define the asyncio event loop fixture.
# This ensures pytest-asyncio has the correct event loop for async fixtures.
@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest-asyncio's default loop to ensure it's closed properly."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# 2. Mock Database Session Fixture
# We are no longer setting up a real database. We're mocking the session directly.
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncMock, None]: # Type hint as AsyncMock
    """
    Provides a mock asynchronous session for testing,
    simulating database interactions without a real database.
    """
    mock_session = AsyncMock() # Create an asynchronous mock object for the session

    # You might want to define some common behaviors for your mock session
    # For example, ensure session.commit() is awaitable and does nothing
    mock_session.commit.return_value = None # commit doesn't return anything
    mock_session.rollback.return_value = None # rollback doesn't return anything
    mock_session.refresh.return_value = None # refresh doesn't return anything

    # For .execute(), you'll likely want it to return a mock result object
    # For now, let's make it an AsyncMock that returns an empty list for simplicity
    mock_session.execute.return_value = AsyncMock(scalars=MagicMock(all=MagicMock(return_value=[])))

    yield mock_session
    # Clean up the mock if necessary, though usually not strictly needed for AsyncMock
    mock_session.reset_mock() # Resets calls, return values, etc. for the next test

# 3. FastAPI Test Client Fixture (still needed for API tests)
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncMock) -> AsyncGenerator[httpx.AsyncClient, None]: # Type hint with AsyncMock
    """
    Provides an asynchronous test client for FastAPI,
    with dependency overrides for the database session.
    """
    # Override the get_db dependency to use our *mock* session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create an AsyncClient for testing FastAPI routes
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides after the test
    app.dependency_overrides.clear()