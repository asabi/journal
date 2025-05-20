from fastapi import APIRouter, HTTPException, Depends, Query
import httpx
from core.config import settings

router = APIRouter()

WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"

def get_weather_client():
    """Provides an async HTTP client for weather API requests."""
    return httpx.AsyncClient(timeout=10.0)

@router.get("/current", description="Get the current weather for a specified location.")
async def get_current_weather(
    location: str = Query(..., description="Name of the location to fetch weather for (e.g., 'New York')"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches the current weather data for a given location.

    Parameters:
    - location (str): The name of the location.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing current weather data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/forecast", description="Get the weather forecast for a specified location.")
async def get_weather_forecast(
    location: str = Query(..., description="Name of the location to fetch forecast for"),
    days: int = Query(5, description="Number of days to include in the forecast (default: 5)"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches the weather forecast for a given location.

    Parameters:
    - location (str): The name of the location.
    - days (int): Number of days to include in the forecast.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing forecast data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/marine", description="Get marine weather data for a specified location.")
async def get_marine_weather(
    location: str = Query(..., description="Name of the location to fetch marine weather for"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches marine weather data for a given location.

    Parameters:
    - location (str): The name of the location.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing marine weather data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/alerts", description="Get weather alerts for a specified location.")
async def get_weather_alerts(
    location: str = Query(..., description="Name of the location to fetch alerts for"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches weather alerts for a given location.

    Parameters:
    - location (str): The name of the location.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing weather alerts.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/airquality", description="Get air quality data for a specified location.")
async def get_air_quality(
    location: str = Query(..., description="Name of the location to fetch air quality for"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches air quality data for a given location.

    Parameters:
    - location (str): The name of the location.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing air quality data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/astronomy", description="Get astronomy data for a specified location.")
async def get_astronomy_data(
    location: str = Query(..., description="Name of the location to fetch astronomy data for"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches astronomy data for a given location.

    Parameters:
    - location (str): The name of the location.
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing astronomy data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/history", description="Get historical weather data for a specified location and date.")
async def get_weather_history(
    location: str = Query(..., description="Name of the location to fetch historical data for"),
    date: str = Query(..., description="Date for which to fetch historical data (format: YYYY-MM-DD)"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches historical weather data for a given location and date.

    Parameters:
    - location (str): The name of the location.
    - date (str): Date for which to fetch data (format: YYYY-MM-DD).
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing historical weather data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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

@router.get("/future", description="Get future weather data for a specified location and date.")
async def get_future_weather(
    location: str = Query(..., description="Name of the location to fetch future data for"),
    date: str = Query(..., description="Date for which to fetch future data (format: YYYY-MM-DD)"),
    client: httpx.AsyncClient = Depends(get_weather_client)
):
    """
    Fetches future weather data for a given location and date.

    Parameters:
    - location (str): The name of the location.
    - date (str): Date for which to fetch data (format: YYYY-MM-DD).
    - client (httpx.AsyncClient): Internal HTTP client used to make the request.

    Returns:
    - dict: JSON response from the WeatherAPI containing future weather data.

    Raises:
    - HTTPException: If the API request fails or returns an error.
    """
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
