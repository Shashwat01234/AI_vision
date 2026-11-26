"""
Synchronous SQLAlchemy database engine and session factory.
Fast, reliable, and free of event-loop deadlocks on Windows SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.models import Base

db_path = settings.get_database_path()

# SQLite engine with check_same_thread=False
engine = create_engine(
    f"sqlite:///{db_path.as_posix()}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all database tables synchronously."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
