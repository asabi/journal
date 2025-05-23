from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True)
    data_type = Column(String, index=True)  # e.g., "heart_rate", "steps", "alert"
    value = Column(Float)  # For numeric values
    text_value = Column(String)  # For string-based values (e.g., alerts)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)  # Store the entire JSON payload


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
