from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Get the URL from the environment variable (defined in docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency to get the DB session in your endpoints
async def get_db():
    async with SessionLocal() as session:
        yield session