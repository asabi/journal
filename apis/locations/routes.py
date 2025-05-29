from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db, LocationTrack
from apis.locations.schemas import OwnTracksPayload, LocationTrackResponse
from apis.weather.routes import post_all_weather_data
from datetime import datetime, timedelta
import httpx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

router = APIRouter()


def get_city_from_coordinates(lat: float, lon: float) -> str:
    """Get city name from coordinates using Nominatim geocoder"""
    try:
        geolocator = Nominatim(user_agent="life_journal")
        location = geolocator.reverse(f"{lat}, {lon}", language="en")
        address = location.raw.get("address", {})

        # Try different address components in order of preference
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("suburb")
            or address.get("county")
        )
        return city if city else "Unknown"
    except (GeocoderTimedOut, Exception) as e:
        print(f"Geocoding error: {str(e)}")
        return "Unknown"


@router.post("/track", response_model=LocationTrackResponse)
async def track_location(
    payload: OwnTracksPayload,
    db: Session = Depends(get_db),
):
    """
    Handle location updates from OwnTracks app.
    If the city has changed or it's been more than 1 hour since the last weather check,
    fetch new weather data for the location.
    """
    try:
        # Get city name from coordinates
        city = get_city_from_coordinates(payload.lat, payload.lon)

        # Create location track entry
        location_track = LocationTrack(
            timestamp=datetime.fromtimestamp(payload.tst) if payload.tst else datetime.utcnow(),
            lat=payload.lat,
            lon=payload.lon,
            alt=payload.alt,
            acc=payload.acc,
            batt=payload.batt,
            vel=payload.vel,
            tid=payload.tid,
            city=city,
        )

        db.add(location_track)
        db.commit()
        db.refresh(location_track)

        # Check if we need to update weather data
        should_update_weather = False

        # Get the last location entry for this tracker
        last_location = (
            db.query(LocationTrack)
            .filter(LocationTrack.tid == payload.tid, LocationTrack.id != location_track.id)
            .order_by(LocationTrack.timestamp.desc())
            .first()
        )

        if last_location:
            # Update weather if:
            # 1. City has changed, or
            # 2. No weather check in the last hour, or
            # 3. No previous weather check at all
            should_update_weather = (
                last_location.city != city
                or not last_location.last_weather_check
                or datetime.utcnow() - last_location.last_weather_check > timedelta(hours=1)
            )
        else:
            # First entry for this tracker, get weather
            should_update_weather = True

        if should_update_weather:
            try:
                # Create a new HTTP client for weather API
                async with httpx.AsyncClient() as client:
                    # Fetch weather data
                    await post_all_weather_data(location=city, client=client, db=db)

                # Update last_weather_check timestamp
                location_track.last_weather_check = datetime.utcnow()
                db.commit()
                db.refresh(location_track)

            except Exception as e:
                print(f"Error fetching weather data: {str(e)}")
                # Continue even if weather fetch fails
                pass

        return location_track

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=list[LocationTrackResponse])
async def get_location_history(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db),
):
    """Get location history within a time range"""
    query = db.query(LocationTrack)

    if start_time:
        query = query.filter(LocationTrack.timestamp >= start_time)
    if end_time:
        query = query.filter(LocationTrack.timestamp <= end_time)

    return query.order_by(LocationTrack.timestamp.desc()).all()
