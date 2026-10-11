"""Database session configuration and initialization."""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATA_DIR, DATABASE_URL
from app.db.base import Base

# Ensure dedicated backend data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create SQLite engine
# check_same_thread=False is needed for SQLite when used with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory for handling database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session per request,
    closing it cleanly once the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined in models if they do not exist.
    Import models here so Base knows about all registered metadata.
    """
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
