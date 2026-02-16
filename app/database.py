from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Database connection URL retrieved from Docker environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize the Asynchronous SQL Engine
# echo=True enables SQL logging for development transparency
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory specifically for AsyncSessions
# expire_on_commit=False prevents SQLAlchemy from re-fetching objects 
# automatically, which is essential for stable async operations.
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency to provide a scoped database session in FastAPI endpoints.
# Ensures the session is properly closed after each request.
async def get_db():
    async with SessionLocal() as session:
        yield session
