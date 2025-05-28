# core/db.py (updated with upsert)
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy import insert as generic_insert
from sqlalchemy.inspection import inspect
from datetime import datetime
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)  # connect_args={"check_same_thread": False}
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_upsert_statement(model_class, data, conflict_keys, update_keys):
    dialect = engine.dialect.name

    if dialect == "sqlite":
        insert_stmt = sqlite.insert(model_class).values(**data)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=conflict_keys,
            set_={key: data[key] for key in update_keys if key in data},
        )
    elif dialect == "postgresql":
        insert_stmt = postgresql.insert(model_class).values(**data)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=conflict_keys,
            set_={key: data[key] for key in update_keys if key in data},
        )
    else:
        raise NotImplementedError(f"Upsert not implemented for dialect {dialect}")

    return insert_stmt


class User(Base):
    __tablename__ = "health_user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)


class HealthData(Base):
    __tablename__ = "health_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("health_user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    units = Column(String)
    name = Column(String)
    user = relationship(User)

    __table_args__ = (UniqueConstraint("user_id", "timestamp", "name", name="uq_healthdata_user_time_name"),)


class BaseMetric:
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def health_data_id(cls):
        return Column(Integer, ForeignKey("health_data.id"), unique=True)

    @declared_attr
    def value(cls):
        return Column(Float)

    @declared_attr
    def units(cls):
        return Column(String)

    @declared_attr
    def source(cls):
        return Column(String)

    @declared_attr
    def health_data(cls):
        return relationship("HealthData")


# Common metrics (shared upsert logic)
class Steps(BaseMetric, Base):
    __tablename__ = "health_steps"


class ActiveEnergy(BaseMetric, Base):
    __tablename__ = "health_active_energy"


class AppleStandTime(BaseMetric, Base):
    __tablename__ = "health_apple_stand_time"


class AppleExerciseTime(BaseMetric, Base):
    __tablename__ = "health_apple_exercise_time"


class HeadphoneAudioExposure(BaseMetric, Base):
    __tablename__ = "health_headphone_audio_exposure"


class SixMinuteWalkingTestDistance(BaseMetric, Base):
    __tablename__ = "health_six_minute_walking_test_distance"


class WalkingRunningDistance(BaseMetric, Base):
    __tablename__ = "health_walking_running_distance"


class WalkingStepLength(BaseMetric, Base):
    __tablename__ = "health_walking_step_length"


class WalkingDoubleSupportPercentage(BaseMetric, Base):
    __tablename__ = "health_walking_double_support_percentage"


class WalkingAsymmetryPercentage(BaseMetric, Base):
    __tablename__ = "health_walking_asymmetry_percentage"


class RestingHeartRate(BaseMetric, Base):
    __tablename__ = "health_resting_heart_rate"


class BasalEnergyBurned(BaseMetric, Base):
    __tablename__ = "health_basal_energy_burned"


class Handwashing(BaseMetric, Base):
    __tablename__ = "health_handwashing"


class StairSpeedDown(BaseMetric, Base):
    __tablename__ = "health_stair_speed_down"


class WalkingSpeed(BaseMetric, Base):
    __tablename__ = "health_walking_speed"


class WalkingHeartRateAvg(BaseMetric, Base):
    __tablename__ = "health_walking_heart_rate_average"


class PhysicalEffort(BaseMetric, Base):
    __tablename__ = "health_physical_effort"


class FlightsClimbed(BaseMetric, Base):
    __tablename__ = "health_flights_climbed"


class HeartRateVariability(BaseMetric, Base):
    __tablename__ = "health_heart_rate_variability"


class RespoitoryRate(BaseMetric, Base):
    __tablename__ = "health_respiratory_rate"


class Vo2Max(BaseMetric, Base):
    __tablename__ = "health_vo2_max"


# Specialized model with extra fields
class HeartRate(BaseMetric, Base):
    __tablename__ = "health_heart_rate"
    units = Column(String, default="bpm")
    min = Column(Float, nullable=True)
    max = Column(Float, nullable=True)
    avg = Column(Float, nullable=True)


class SleepAnalysis(BaseMetric, Base):
    __tablename__ = "health_sleep_analysis"
    core = Column(Float, nullable=True)
    inBedStart = Column(DateTime, nullable=True)
    inBed = Column(Float, nullable=True)
    sleepStart = Column(DateTime, nullable=True)
    rem = Column(Float, nullable=True)
    sleepEnd = Column(DateTime, nullable=True)
    inBedEnd = Column(DateTime, nullable=True)
    awake = Column(Float, nullable=True)
    asleep = Column(Float, nullable=True)
    deep = Column(Float, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upsert_model(db, model_class, data, conflict_keys, update_keys):
    stmt = get_upsert_statement(model_class, data, conflict_keys, update_keys)
    db.execute(stmt)


def save_metric(db, user_id, metric_name, metric_units, data_item, model_class):
    # Upsert HealthData first
    health_data_dict = {
        "user_id": user_id,
        "timestamp": data_item["date"],
        "name": metric_name,
        "units": metric_units,
    }

    upsert_model(
        db,
        model_class=HealthData,
        data=health_data_dict,
        conflict_keys=["user_id", "timestamp", "name"],
        update_keys=["units"],
    )

    db.commit()

    health_data = (
        db.query(HealthData).filter_by(user_id=user_id, timestamp=data_item["date"], name=metric_name).first()
    )

    # Upsert Metric
    model_columns = {c.key for c in inspect(model_class).columns}
    model_data = {k: v for k, v in data_item.items() if k in model_columns}
    model_data["health_data_id"] = health_data.id
    model_data["units"] = metric_units

    upsert_model(
        db,
        model_class=model_class,
        data=model_data,
        conflict_keys=["health_data_id"],
        update_keys=list(model_data.keys()),
    )

    db.commit()
