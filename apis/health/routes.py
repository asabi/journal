from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime
from core.db import User
from core.db import (
    get_db,
    save_metric,
    HeartRate,
    Steps,
    SleepAnalysis,
    ActiveEnergy,
    AppleStandTime,
    AppleStandHour,
    AppleStairSpeedUp,
    AppleExerciseTime,
    HeadphoneAudioExposure,
    SixMinuteWalkingTestDistance,
    WalkingRunningDistance,
    RestingHeartRate,
    BasalEnergyBurned,
    Handwashing,
    StairSpeedDown,
    WalkingHeartRateAvg,
    FlightsClimbed,
    HeartRateVariability,
    Vo2Max,
    RespoitoryRate,
    WalkingStepLength,
    WalkingDoubleSupportPercentage,
    WalkingAsymmetryPercentage,
    WalkingSpeed,
    PhysicalEffort,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class DataItem(BaseModel):
    qty: Optional[float] = None
    source: Optional[str] = None
    date: Optional[datetime] = None
    Max: Optional[float] = None
    Min: Optional[float] = None
    Avg: Optional[float] = None
    inBedStart: Optional[datetime] = None
    inBed: Optional[float] = None
    sleepStart: Optional[datetime] = None
    sleepEnd: Optional[datetime] = None
    inBedEnd: Optional[datetime] = None
    awake: Optional[float] = None
    asleep: Optional[float] = None
    deep: Optional[float] = None
    rem: Optional[float] = None
    core: Optional[float] = None

    @field_validator("date", "inBedStart", "sleepStart", "sleepEnd", "inBedEnd", mode="before")
    def parse_datetime(cls, value):
        if value:
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None
        return None


class Metric(BaseModel):
    data: List[DataItem]
    name: str
    units: str


class Metrics(BaseModel):
    metrics: List[Metric]


class Payload(BaseModel):
    data: Metrics


METRIC_MODEL_MAP = {
    "heart_rate": HeartRate,
    "step_count": Steps,
    "sleep_analysis": SleepAnalysis,
    "active_energy": ActiveEnergy,
    "apple_stand_time": AppleStandTime,
    "apple_exercise_time": AppleExerciseTime,
    "headphone_audio_exposure": HeadphoneAudioExposure,
    "six_minute_walking_test_distance": SixMinuteWalkingTestDistance,
    "walking_running_distance": WalkingRunningDistance,
    "walking_heart_rate_average": WalkingHeartRateAvg,
    "resting_heart_rate": RestingHeartRate,
    "basal_energy_burned": BasalEnergyBurned,
    "handwashing": Handwashing,
    "stair_speed_down": StairSpeedDown,
    "flights_climbed": FlightsClimbed,
    "heart_rate_variability": HeartRateVariability,
    "vo2_max": Vo2Max,
    "respiratory_rate": RespoitoryRate,
    "environmental_audio_exposure": HeadphoneAudioExposure,
    "walking_step_length": WalkingStepLength,
    "walking_double_support_percentage": WalkingDoubleSupportPercentage,
    "walking_asymmetry_percentage": WalkingAsymmetryPercentage,
    "walking_speed": WalkingSpeed,
    "physical_effort": PhysicalEffort,
}

FIELD_ALIASES = {
    "Min": "min",
    "Max": "max",
    "Avg": "avg",
    "qty": "value",
}


@router.post("/")
async def post_health_data(data: Payload, db: Session = Depends(get_db)):
    user_id = 1  # TODO: replace with real user context
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, username="asabi")
        db.add(user)
        db.commit()
    for metric in data.data.metrics:
        logger.info(f"Processing metric: {metric.name}")
        model_class = METRIC_MODEL_MAP.get(metric.name)
        if not model_class:
            logger.warning(f"Unknown metric name: {metric.name}")
            continue

        model_columns = {c.key for c in model_class.__table__.columns}

        for data_item in metric.data:
            parsed_item = {}
            for field_name, value in data_item.dict().items():
                normalized_key = FIELD_ALIASES.get(field_name, FIELD_ALIASES.get(field_name.lower(), field_name))
                if normalized_key in model_columns:
                    parsed_item[normalized_key] = value

            parsed_item["date"] = data_item.date  # Required for HealthData upsert
            save_metric(db, user_id, metric.name, metric.units, parsed_item, model_class)

    return {"status": "success"}


@router.get("/")
async def get_health_data(db: Session = Depends(get_db)):
    health_data = db.query(HealthData).all()
    return health_data


@router.get("/activity")
def get_activity_summary():
    return {"message": "Activity summary endpoint"}
