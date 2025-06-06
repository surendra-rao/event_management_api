from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from config import settings

# Create an asynchronous engine
engine = create_async_engine(settings.DATABASE_URL, echo=True) # echo=True for logging SQL queries

# Create a session local factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession, # Use AsyncSession for asynchronous operations
    expire_on_commit=False # Prevents objects from being expired after commit
)

# Base class for our declarative models
Base = declarative_base()

async def get_db():
    """
    Dependency to provide a database session for API routes.
    Ensures the session is closed after the request.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    """
    Initializes the database by creating all tables.
    Should be called once on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created.")