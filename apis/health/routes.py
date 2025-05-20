from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.db import HealthData, get_db
from sqlalchemy.orm import Session
from datetime import datetime


router = APIRouter()

# Pydantic model for incoming health data
class HealthDataIn(BaseModel):
    data_type: str
    value: Optional[float] = None
    text_value: Optional[str] = None


@router.post("/")
async def post_health_data(data: HealthDataIn, db: Session = Depends(get_db)):
    """
    Accepts health data in JSON format and stores it in the database.
    """
    db_data = HealthData(
        data_type=data.data_type,
        value=data.value,
        text_value=data.text_value,
        timestamp=datetime.utcnow()
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return {"status": "success", "data": db_data}


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
