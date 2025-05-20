from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_weather():
    return {"message": "Weather endpoint - not implemented yet"}

@router.get("/forecast")
def get_weather_forecast():
    return {"message": "Weather forecast endpoint - not implemented yet"}
