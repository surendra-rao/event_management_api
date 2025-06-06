import asyncio
from database import init_db # Import the init_db function
# Import your models to ensure they are registered with Base.metadata
from app.models import Event, Attendee

async def main():
    await init_db()

if __name__ == "__main__":
    print("Attempting to create database tables...")
    asyncio.run(main())
    print("Database table creation process completed. Check your database for 'events' and 'attendees' tables.")