from fastapi import APIRouter, HTTPException, Depends
import httpx
from core.config import settings

router = APIRouter()

WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"

def get_weather_client():
    return httpx.AsyncClient(timeout=10.0)

@router.get("/current")
async def get_current_weather(location: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_weather_forecast(location: str, days: int = 5, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/forecast.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "days": days
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marine")
async def get_marine_weather(location: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/marine.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_weather_alerts(location: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/alerts.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airquality")
async def get_air_quality(location: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "aqi": "yes"
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/astronomy")
async def get_astronomy_data(location: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/astronomy.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_weather_history(location: str, date: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/history.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "dt": date
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/future")
async def get_future_weather(location: str, date: str, client: httpx.AsyncClient = Depends(get_weather_client)):
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/future.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "dt": date
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
