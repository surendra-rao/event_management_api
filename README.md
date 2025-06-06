# Event Management API

## Project Overview

This is a **RESTful API** for managing events and attendees. It provides endpoints for creating, retrieving, updating, and deleting event information, as well as registering and listing attendees for specific events. Built with **FastAPI** and **SQLAlchemy** (with an asynchronous backend), this API aims to provide a robust and efficient solution for event management needs.

## Features

* **Event Management:**
    * Create new events with details like name, location, start/end times, and max capacity.
    * Retrieve event details by ID.
    * List all events, with options for filtering (e.g., upcoming events).
    * Update existing event details.
    * Delete events.
* **Attendee Registration:**
    * Register attendees for specific events.
    * List attendees for a given event, with pagination.
    * Count attendees for an event.
* **Database:** Asynchronous ORM interaction using SQLAlchemy 2.0.
* **Validation:** Robust data validation and serialization using Pydantic.
* **Documentation:** Automatic interactive API documentation (Swagger UI / ReDoc) provided by FastAPI.

## Technologies Used

* **Python 3.10+**
* **FastAPI**: For building the web API.
* **SQLAlchemy (2.0 style)**: Asynchronous ORM for database interactions.
* **Alembic**: For database migrations (if implemented).
* **`asyncpg` / `aiosqlite`**: Asynchronous database drivers (e.g., for PostgreSQL or SQLite).
* **Pydantic**: For data validation and settings management.
* **Uvicorn**: ASGI server for running the FastAPI application.
* **`pytest`**: For testing.
* **`pytest-asyncio`**: For running asynchronous tests with `pytest`.
* **`httpx`**: Asynchronous HTTP client for API testing.
* **`Faker`**: For generating fake data in tests.
* **`black` / `isort`**: For code formatting and import sorting (recommended).

## Setup and Installation

Follow these steps to get a development environment up and running on your local machine.

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd event_management_api # Or whatever your project folder is named
```
### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```Bash
pip install -r requirements.txt
```

### 4. Database Setup

This project uses SQLAlchemy for database interactions.
- Development Database (e.g., SQLite):
  For quick local development and testing, you can use SQLite.

  - Ensure aiosqlite is installed: pip install aiosqlite
  - The database.py file should be configured to connect to your SQLite file.
- Production/Persistent Database (e.g., PostgreSQL):
  For a more robust setup, you might use PostgreSQL.
  - Ensure asyncpg is installed: pip install asyncpg
  - Update the DATABASE_URL in your .env file (or config.py) to connect to your PostgreSQL instance.
  - Database Migrations (Alembic - if applicable): If you are using Alembic for migrations:
    ```Bash
    # Initialize Alembic (only once, if you haven't already)
    # alembic init -t async alembic

    # Generate a new migration (after model changes)
    # alembic revision --autogenerate -m "Add initial tables"

    # Apply migrations
    # alembic upgrade head
    ```

## Running the Application

### 1. Configure Environment Variables
Create a .env file in the root of your project and add necessary environment variables, such as your database URL.

```Bash
# .env
DATABASE_URL="sqlite+aiosqlite:///./test.db" # Example for SQLite
# DATABASE_URL="postgresql+asyncpg://user:password@host:port/database_name" # Example for PostgreSQL
```

### 2. Start the API Server
```Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API will be running at http://127.0.0.1:8000.

## API Documentation
FastAPI automatically generates interactive API documentation.

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Running Tests
To run the test suite:
```Bash
pytest
```
Ensure you have pytest and pytest-asyncio installed (pip install pytest pytest-asyncio).
Also, make sure your pytest.ini is configured for asyncio_mode = auto:

```Ini, TOML
# pytest.ini
[pytest]
asyncio_mode = auto
```

## Project Structure
A brief overview of the key directories and files:

```
event_management_api/
├── app/
│   ├── __init__.py
│   ├── crud/            # Create, Read, Update, Delete operations (repositories)
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas for data validation and serialization
│   └── services.py             # API endpoints (routers)
├── database.py          # Database connection and session management
├── main.py              # FastAPI application entry , point API endpoints (routers)
├── tests/
│   ├── __init__.py
│   ├── test_models_and_schemas.py
│   ├── test_repositories.py
│   └── conftest.py      # Pytest fixtures for testing
├── .env.example         # Example environment variables
├── requirements.txt     # Project dependencies
├── pytest.ini           # Pytest configuration
└── README.md            # This file
```