from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging
from core.db import get_db, HealthData

logger = logging.getLogger(__name__)

router = APIRouter()


class Metric(BaseModel):
    name: str
    value: float


class HealthDataIn(BaseModel):
    heart_rate: Optional[float] = None
    steps: Optional[int] = None
    sleep_analysis: Optional[str] = None
    active_energy: Optional[int] = None
    apple_stand_time: Optional[int] = None
    apple_exercise_time: Optional[int] = None
    headphone_audio_exposure: Optional[int] = None
    six_minute_walking_test_distance: Optional[float] = None
    walking_running_distance: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    basal_energy_burned: Optional[int] = None
    handwashing: Optional[int] = None


@router.post("/")
async def post_health_data(data: HealthDataIn, db: Session = Depends(get_db)):
    try:
        health_data = HealthData(
            heart_rate=data.heart_rate,
            steps=data.steps,
            sleep_analysis=data.sleep_analysis,
            active_energy=data.active_energy,
            apple_stand_time=data.apple_stand_time,
            apple_exercise_time=data.apple_exercise_time,
            headphone_audio_exposure=data.headphone_audio_exposure,
            six_minute_walking_test_distance=data.six_minute_walking_test_distance,
            walking_running_distance=data.walking_running_distance,
            resting_heart_rate=data.resting_heart_rate,
            basal_energy_burned=data.basal_energy_burned,
            handwashing=data.handwashing,
        )
        db.add(health_data)
        db.commit()
        db.refresh(health_data)
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error posting health data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/")
async def get_health_data(db: Session = Depends(get_db)):
    health_data = db.query(HealthData).all()
    return health_data


@router.get("/activity")
def get_activity_summary():
    return {"message": "Activity summary endpoint"}
