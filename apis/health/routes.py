from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.db import HealthData, get_db, HeartRate, Steps, SleepAnalysis, ActiveEnergy, AppleStandTime, AppleExerciseTime, HeadphoneAudioExposure, SixMinuteWalkingTestDistance, WalkingRunningDistance, RestingHeartRate, BasalEnergyBurned, Handwashing
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import Json

router = APIRouter()


class HealthDataIn(BaseModel):
    data_type: str
    value: Optional[float] = None
    json_data: Optional[Json] = None


@router.post("/")
async def post_health_data(data: HealthDataIn, db: Session = Depends(get_db)):
    """
    Accepts health data in JSON format and stores it in the database.
    """
    health_data = HealthData(data_type=data.data_type)
    db.add(health_data)
    db.commit()
    db.refresh(health_data)

    if data.value is not None:
        if data.data_type == "heart_rate":
            heart_rate = HeartRate(health_data_id=health_data.id, value=data.value)
            db.add(heart_rate)
        elif data.data_type == "steps":
            steps = Steps(health_data_id=health_data.id, value=int(data.value))
            db.add(steps)
        elif data.data_type == "active_energy":
            active_energy = ActiveEnergy(health_data_id=health_data.id, value=data.value)
            db.add(active_energy)
        elif data.data_type == "apple_stand_time":
            apple_stand_time = AppleStandTime(health_data_id=health_data.id, value=data.value)
            db.add(apple_stand_time)
        elif data.data_type == "apple_exercise_time":
            apple_exercise_time = AppleExerciseTime(health_data_id=health_data.id, value=data.value)
            db.add(apple_exercise_time)
        elif data.data_type == "headphone_audio_exposure":
            headphone_audio_exposure = HeadphoneAudioExposure(health_data_id=health_data.id, value=data.value)
            db.add(headphone_audio_exposure)
        elif data.data_type == "six_minute_walking_test_distance":
            six_minute_walking_test_distance = SixMinuteWalkingTestDistance(health_data_id=health_data.id, value=data.value)
            db.add(six_minute_walking_test_distance)
        elif data.data_type == "walking_running_distance":
            walking_running_distance = WalkingRunningDistance(health_data_id=health_data.id, value=data.value)
            db.add(walking_running_distance)
        elif data.data_type == "resting_heart_rate":
            resting_heart_rate = RestingHeartRate(health_data_id=health_data.id, value=data.value)
            db.add(resting_heart_rate)
        elif data.data_type == "basal_energy_burned":
            basal_energy_burned = BasalEnergyBurned(health_data_id=health_data.id, value=data.value)
            db.add(basal_energy_burned)
        elif data.data_type == "handwashing":
            handwashing = Handwashing(health_data_id=health_data.id, value=data.value)
            db.add(handwashing)
        else:
            # Handle other data types as needed
            pass

    if data.json_data:
        sleep_analysis = SleepAnalysis(health_data_id=health_data.id, data=data.json_data)
        db.add(sleep_analysis)

    db.commit()

    return {"status": "success", "data": health_data}


@router.get("/")
async def get_health_data(db: Session = Depends(get_db)):
    """
    Returns all stored health data.
    """
    data = db.query(HealthData).all()
    return {"status": "success", "data": data}


@router.get("/activity")
def get_activity_summary():
    return {"message": "Activity summary endpoint - not implemented yet"}
