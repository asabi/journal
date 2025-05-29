from fastapi import APIRouter, HTTPException, Depends, Query
import httpx
from core.config import settings
from sqlalchemy.orm import Session
from core.db import get_db, WeatherData, WeatherAlerts, AirQuality, MarineWeather, AstronomyData
from typing import Dict, Any, List, Union
from apis.weather.schemas import (
    WeatherDataSchema,
    WeatherAlertSchema,
    AirQualitySchema,
    MarineWeatherSchema,
    AstronomyDataSchema,
    AllWeatherDataResponse,
)
from datetime import datetime

router = APIRouter()

WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"


def get_weather_client():
    """Provides an async HTTP client for weather API requests."""
    return httpx.AsyncClient(timeout=10.0)


@router.post("/current", description="Get the current weather for a specified location and save to database.")
async def post_current_weather(
    location: str = Query(..., description="Name of the location to fetch weather for (e.g., 'New York')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
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
            f"{WEATHER_API_BASE_URL}/current.json", params={"key": settings.WEATHER_API_KEY, "q": location}
        )
        response.raise_for_status()
        weather_data = response.json()

        # Store the weather data in the database
        weather_entry = WeatherData(
            location_name=weather_data["location"]["name"],
            location_region=weather_data["location"]["region"],
            location_country=weather_data["location"]["country"],
            location_lat=weather_data["location"]["lat"],
            location_lon=weather_data["location"]["lon"],
            last_updated_epoch=weather_data["location"]["localtime_epoch"],
            last_updated=weather_data["location"]["localtime"],
            temp_c=weather_data["current"]["temp_c"],
            temp_f=weather_data["current"]["temp_f"],
            condition_text=weather_data["current"]["condition"]["text"],
            condition_icon=weather_data["current"]["condition"]["icon"],
            condition_code=weather_data["current"]["condition"]["code"],
            wind_mph=weather_data["current"]["wind_mph"],
            wind_kph=weather_data["current"]["wind_kph"],
            wind_degree=weather_data["current"]["wind_degree"],
            wind_dir=weather_data["current"]["wind_dir"],
            pressure_mb=weather_data["current"]["pressure_mb"],
            pressure_in=weather_data["current"]["pressure_in"],
            precip_mm=weather_data["current"]["precip_mm"],
            precip_in=weather_data["current"]["precip_in"],
            humidity=weather_data["current"]["humidity"],
            cloud=weather_data["current"]["cloud"],
            feelslike_c=weather_data["current"]["feelslike_c"],
            feelslike_f=weather_data["current"]["feelslike_f"],
            windchill_c=weather_data["current"]["windchill_c"],
            windchill_f=weather_data["current"]["windchill_f"],
            heatindex_c=weather_data["current"]["heatindex_c"],
            heatindex_f=weather_data["current"]["heatindex_f"],
            dewpoint_c=weather_data["current"]["dewpoint_c"],
            dewpoint_f=weather_data["current"]["dewpoint_f"],
            vis_km=weather_data["current"]["vis_km"],
            vis_miles=weather_data["current"]["vis_miles"],
            uv=weather_data["current"]["uv"],
            gust_mph=weather_data["current"]["gust_mph"],
            gust_kph=weather_data["current"]["gust_kph"],
        )

        db.add(weather_entry)
        db.commit()
        db.refresh(weather_entry)

        return weather_entry

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts", description="Get weather alerts for a specified location and save to database.")
async def post_weather_alerts(
    location: str = Query(..., description="Name of the location to fetch alerts for (e.g., 'New York')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
):
    """
    Fetches weather alerts for a given location.
    """
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/forecast.json",
            params={"key": settings.WEATHER_API_KEY, "q": location, "alerts": "yes"},
        )
        response.raise_for_status()
        data = response.json()

        if "alerts" in data and "alert" in data["alerts"]:
            alerts = []
            for alert in data["alerts"]["alert"]:
                alert_entry = WeatherAlerts(
                    location_name=data["location"]["name"],
                    headline=alert.get("headline"),
                    severity=alert.get("severity"),
                    urgency=alert.get("urgency"),
                    areas=alert.get("areas"),
                    category=alert.get("category"),
                    certainty=alert.get("certainty"),
                    event=alert.get("event"),
                    note=alert.get("note"),
                    effective=alert.get("effective"),
                    expires=alert.get("expires"),
                    desc=alert.get("desc"),
                    instruction=alert.get("instruction"),
                )
                db.add(alert_entry)
                alerts.append(alert_entry)

            db.commit()
            for alert in alerts:
                db.refresh(alert)
            return alerts
        return {"message": "No alerts found for this location"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/air-quality", description="Get air quality data for a specified location and save to database.")
async def post_air_quality(
    location: str = Query(..., description="Name of the location to fetch air quality for (e.g., 'New York')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
):
    """
    Fetches air quality data for a given location.
    """
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/current.json",
            params={"key": settings.WEATHER_API_KEY, "q": location, "aqi": "yes"},
        )
        response.raise_for_status()
        data = response.json()

        if "air_quality" in data["current"]:
            aqi_data = data["current"]["air_quality"]
            aqi_entry = AirQuality(
                location_name=data["location"]["name"],
                last_updated=data["current"]["last_updated"],
                co=aqi_data.get("co"),
                no2=aqi_data.get("no2"),
                o3=aqi_data.get("o3"),
                so2=aqi_data.get("so2"),
                pm2_5=aqi_data.get("pm2_5"),
                pm10=aqi_data.get("pm10"),
                us_epa_index=aqi_data.get("us-epa-index"),
                gb_defra_index=aqi_data.get("gb-defra-index"),
            )
            db.add(aqi_entry)
            db.commit()
            db.refresh(aqi_entry)
            return aqi_entry
        return {"message": "No air quality data available for this location"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marine", description="Get marine weather data for a specified location and save to database.")
async def post_marine_weather(
    location: str = Query(..., description="Name of the location to fetch marine data for (e.g., 'Sydney')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
):
    """
    Fetches marine weather data for a given location.
    """
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/marine.json",
            params={"key": settings.WEATHER_API_KEY, "q": location, "tides": "yes"},
        )
        response.raise_for_status()
        data = response.json()

        if "tide" in data:
            marine_entries = []
            for tide_data in data["tide"]["tide"]:
                marine_entry = MarineWeather(
                    location_name=data["location"]["name"],
                    last_updated=data["current"]["last_updated"],
                    tide_time=tide_data.get("time"),
                    tide_height_mt=tide_data.get("tide_height_mt"),
                    tide_type=tide_data.get("tide_type"),
                    swell_height_m=data["current"].get("swell_height_m"),
                    swell_direction=data["current"].get("swell_dir"),
                    swell_direction_degrees=data["current"].get("swell_dir_degrees"),
                    swell_period_seconds=data["current"].get("swell_period_secs"),
                    water_temp_c=data["current"].get("water_temp_c"),
                    water_temp_f=data["current"].get("water_temp_f"),
                )
                db.add(marine_entry)
                marine_entries.append(marine_entry)

            db.commit()
            for entry in marine_entries:
                db.refresh(entry)
            return marine_entries
        return {"message": "No marine data available for this location"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/astronomy", description="Get astronomy data for a specified location and save to database.")
async def post_astronomy_data(
    location: str = Query(..., description="Name of the location to fetch astronomy data for (e.g., 'London')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
):
    """
    Fetches astronomy data for a given location.
    """
    try:
        response = await client.get(
            f"{WEATHER_API_BASE_URL}/astronomy.json", params={"key": settings.WEATHER_API_KEY, "q": location}
        )
        response.raise_for_status()
        data = response.json()

        if "astronomy" in data and "astro" in data["astronomy"]:
            astro_data = data["astronomy"]["astro"]
            current_date = datetime.now().strftime("%Y-%m-%d")
            astronomy_entry = AstronomyData(
                location_name=data["location"]["name"],
                date=data["astronomy"].get("date") or current_date,
                sunrise=astro_data.get("sunrise"),
                sunset=astro_data.get("sunset"),
                moonrise=astro_data.get("moonrise"),
                moonset=astro_data.get("moonset"),
                moon_phase=astro_data.get("moon_phase"),
                moon_illumination=astro_data.get("moon_illumination"),
                is_moon_up=astro_data.get("is_moon_up"),
                is_sun_up=astro_data.get("is_sun_up"),
            )
            db.add(astronomy_entry)
            db.commit()
            db.refresh(astronomy_entry)
            return astronomy_entry
        return {"message": "No astronomy data available for this location"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all", description="Get all weather-related data for a specified location and save to database.")
async def post_all_weather_data(
    location: str = Query(..., description="Name of the location to fetch all weather data for (e.g., 'New York')"),
    client: httpx.AsyncClient = Depends(get_weather_client),
    db: Session = Depends(get_db),
) -> AllWeatherDataResponse:
    """
    Fetches all available weather data for a given location, including:
    - Current weather
    - Weather alerts
    - Air quality
    - Marine data
    - Astronomy data
    """
    try:
        result = AllWeatherDataResponse()

        # Fetch current weather
        try:
            current_weather = await post_current_weather(location=location, client=client, db=db)
            if isinstance(current_weather, WeatherData):
                result.current_weather = WeatherDataSchema.from_orm(current_weather)
        except Exception as e:
            print(f"Error fetching current weather: {str(e)}")

        # Fetch weather alerts
        try:
            alerts = await post_weather_alerts(location=location, client=client, db=db)
            if isinstance(alerts, list):
                result.alerts = [WeatherAlertSchema.from_orm(alert) for alert in alerts]
        except Exception as e:
            print(f"Error fetching weather alerts: {str(e)}")

        # Fetch air quality
        try:
            air_quality = await post_air_quality(location=location, client=client, db=db)
            if isinstance(air_quality, AirQuality):
                result.air_quality = AirQualitySchema.from_orm(air_quality)
        except Exception as e:
            print(f"Error fetching air quality data: {str(e)}")

        # Fetch marine data
        try:
            marine = await post_marine_weather(location=location, client=client, db=db)
            if isinstance(marine, list):
                result.marine = [MarineWeatherSchema.from_orm(entry) for entry in marine]
        except Exception as e:
            print(f"Error fetching marine data: {str(e)}")

        # Fetch astronomy data
        try:
            astronomy = await post_astronomy_data(location=location, client=client, db=db)
            if isinstance(astronomy, AstronomyData):
                result.astronomy = AstronomyDataSchema.from_orm(astronomy)
        except Exception as e:
            print(f"Error fetching astronomy data: {str(e)}")

        # Check if we got any data
        if all(
            v is None
            for v in [result.current_weather, result.alerts, result.air_quality, result.marine, result.astronomy]
        ):
            raise HTTPException(status_code=500, detail="Failed to fetch any weather data for the specified location")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
