from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.db import HealthData, get_db, HeartRate, Steps, SleepAnalysis
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
