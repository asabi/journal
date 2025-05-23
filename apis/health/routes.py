from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.db import HealthData, get_db
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import Json

router = APIRouter()


class HealthDataIn(BaseModel):
    data: Json


@router.post("/")
async def post_health_data(data: HealthDataIn, db: Session = Depends(get_db)):
    """
    Accepts health data in JSON format and stores it in the database.
    """
    db_data = HealthData(
        data_type="health_data",
        data=data.data,
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
