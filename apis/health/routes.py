from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# In-memory storage for health data
health_data_store: List[BaseModel] = []

# Pydantic model for incoming health data
class HealthData(BaseModel):
    heart_rate: float
    steps: int
    alerts: List[str]

@router.post("/")
async def post_health_data(data: HealthData):
    """
    Accepts health data in JSON format and stores it in memory.
    """
    health_data_store.append(data)
    return {"status": "success", "data": data}

@router.get("/")
async def get_health_data():
    """
    Returns all stored health data.
    """
    return {"status": "success", "data": health_data_store}

@router.get("/activity")
def get_activity_summary():
    return {"message": "Activity summary endpoint - not implemented yet"}
