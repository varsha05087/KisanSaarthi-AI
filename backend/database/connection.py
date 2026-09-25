from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Path to SQLite database file in backend root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "kisansaarthi.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# SQLite requires check_same_thread=False for multithreaded FastAPI access
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    Ensures session is always closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initializes database tables if they do not exist.
    Preserves all existing tables and data across restarts.
    """
    # Import models to ensure they are registered on Base.metadata
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
