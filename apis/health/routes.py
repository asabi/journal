from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.db import HealthData, get_db, HeartRate, Steps, SleepAnalysis, ActiveEnergy, AppleStandTime, AppleExerciseTime, HeadphoneAudioExposure, SixMinuteWalkingTestDistance, WalkingRunningDistance, RestingHeartRate, BasalEnergyBurned, Handwashing
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import Json, ValidationError
import logging
import logging_config

logger = logging.getLogger(__name__)

router = APIRouter()


class Metric(BaseModel):
    name: str
    units: Optional[str] = None
    data: List[dict]


class HealthDataIn(BaseModel):
    metrics: List[Metric]


@router.post("/")
async def post_health_data(data: HealthDataIn, db: Session = Depends(get_db)):
    """
    Accepts health data in JSON format and stores it in the database.
    """
    logger.info(f"Received request data: {data}")  # Log the request data
    try:
        for metric in data.metrics:
            if metric.name == "active_energy":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "sleep_analysis":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "apple_stand_time":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "six_minute_walking_test_distance":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "step_count":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "walking_running_distance":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            elif metric.name == "handwashing":
                for item in metric.data:
                    health_data = HealthData(data_type=metric.name)
                    db.add(health_data)
                    db.commit()
                    db.refresh(health_data)
            else:
                pass

        return {"status": "success"}

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        return {"status": "error", "errors": e.errors()}
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": str(e)}


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
