from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)


class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    data_type = Column(String)  # e.g., "heart_rate", "steps"

    user = relationship(User)


class HeartRate(Base):
    __tablename__ = "heart_rate"

    id = Column(Integer, primary_key=True)
    health_data_id = Column(Integer, ForeignKey('health_data.id'))
    value = Column(Float)

    health_data = relationship(HealthData)


class Steps(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True)
    health_data_id = Column(Integer, ForeignKey('health_data.id'))
    value = Column(Integer)

    health_data = relationship(HealthData)


class SleepAnalysis(Base):
    __tablename__ = "sleep_analysis"

    id = Column(Integer, primary_key=True)
    health_data_id = Column(Integer, ForeignKey('health_data.id'))
    data = Column(JSON)

    health_data = relationship(HealthData)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
