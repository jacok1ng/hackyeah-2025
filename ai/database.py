from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./transportation.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def init_db_with_data():
    """
    Initialize database with tables and system data.
    This ensures vehicle types are always present.
    """
    from init_data import init_vehicle_types

    # Create tables
    init_db()

    # Initialize vehicle types
    db = SessionLocal()
    try:
        init_vehicle_types(db)
    finally:
        db.close()
