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


class WeatherAlerts(Base):
    __tablename__ = "weather_alerts"
    id = Column(Integer, primary_key=True)
    location_name = Column(String)
    headline = Column(String)
    severity = Column(String)
    urgency = Column(String)
    areas = Column(String)
    category = Column(String)
    certainty = Column(String)
    event = Column(String)
    note = Column(String)
    effective = Column(String)
    expires = Column(String)
    desc = Column(String)
    instruction = Column(String)


class AirQuality(Base):
    __tablename__ = "air_quality"
    id = Column(Integer, primary_key=True)
    location_name = Column(String)
    last_updated = Column(String)
    co = Column(Float)  # Carbon Monoxide (μg/m3)
    no2 = Column(Float)  # Nitrogen dioxide (μg/m3)
    o3 = Column(Float)  # Ozone (μg/m3)
    so2 = Column(Float)  # Sulphur dioxide (μg/m3)
    pm2_5 = Column(Float)  # PM2.5 (μg/m3)
    pm10 = Column(Float)  # PM10 (μg/m3)
    us_epa_index = Column(Integer)  # US EPA standard
    gb_defra_index = Column(Integer)  # UK DEFRA standard


class MarineWeather(Base):
    __tablename__ = "marine_weather"
    id = Column(Integer, primary_key=True)
    location_name = Column(String)
    last_updated = Column(String)
    tide_time = Column(String)
    tide_height_mt = Column(Float)
    tide_type = Column(String)  # high or low
    swell_height_m = Column(Float)
    swell_direction = Column(String)
    swell_direction_degrees = Column(Integer)
    swell_period_seconds = Column(Integer)
    water_temp_c = Column(Float)
    water_temp_f = Column(Float)


class AstronomyData(Base):
    __tablename__ = "astronomy_data"
    id = Column(Integer, primary_key=True)
    location_name = Column(String)
    date = Column(String)
    sunrise = Column(String)
    sunset = Column(String)
    moonrise = Column(String)
    moonset = Column(String)
    moon_phase = Column(String)
    moon_illumination = Column(Integer)
    is_moon_up = Column(Integer)
    is_sun_up = Column(Integer)


class LocationTrack(Base):
    __tablename__ = "location_tracks"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    lat = Column(Float)
    lon = Column(Float)
    alt = Column(Float, nullable=True)
    acc = Column(Float, nullable=True)  # Accuracy in meters
    batt = Column(Integer, nullable=True)  # Battery percentage
    vel = Column(Float, nullable=True)  # Velocity
    tid = Column(String, nullable=True)  # Tracker ID
    city = Column(String)  # City name (for weather tracking)
    last_weather_check = Column(DateTime, nullable=True)  # Last time weather was checked for this location


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


class WeatherData(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True)
    location_name = Column(String)
    location_region = Column(String)
    location_country = Column(String)
    location_lat = Column(Float)
    location_lon = Column(Float)
    last_updated_epoch = Column(Integer)
    last_updated = Column(String)
    temp_c = Column(Float)
    temp_f = Column(Float)
    condition_text = Column(String)
    condition_icon = Column(String)
    condition_code = Column(Integer)
    wind_mph = Column(Float)
    wind_kph = Column(Float)
    wind_degree = Column(Integer)
    wind_dir = Column(String)
    pressure_mb = Column(Integer)
    pressure_in = Column(Integer)
    precip_mm = Column(Float)
    precip_in = Column(Float)
    humidity = Column(Integer)
    cloud = Column(Integer)
    feelslike_c = Column(Float)
    feelslike_f = Column(Float)
    windchill_c = Column(Float)
    windchill_f = Column(Float)
    heatindex_c = Column(Float)
    heatindex_f = Column(Float)
    dewpoint_c = Column(Float)
    dewpoint_f = Column(Float)
    vis_km = Column(Integer)
    vis_miles = Column(Integer)
    uv = Column(Integer)
    gust_mph = Column(Float)
    gust_kph = Column(Float)
