from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db, LocationTrack
from apis.locations.schemas import OwnTracksPayload, LocationTrackResponse
from apis.weather.routes import post_all_weather_data
from datetime import datetime, timedelta
import httpx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from typing import Dict, Optional

router = APIRouter()


def get_location_details(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Get detailed location information from coordinates using Nominatim geocoder"""
    try:
        geolocator = Nominatim(user_agent="life_journal")
        location = geolocator.reverse(f"{lat}, {lon}", language="en")

        if not location:
            return {
                "city": "Unknown",
                "state_province": None,
                "country": None,
                "country_code": None,
                "postal_code": None,
                "formatted_address": None,
            }

        address = location.raw.get("address", {})

        # Try different address components for city name
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("suburb")
            or address.get("county")
            or "Unknown"
        )

        # Get state/province (different keys in different countries)
        state_province = (
            address.get("state") or address.get("province") or address.get("region") or address.get("state_district")
        )

        return {
            "city": city,
            "state_province": state_province,
            "country": address.get("country"),
            "country_code": address.get("country_code", "").upper(),
            "postal_code": address.get("postcode"),
            "formatted_address": location.address,
        }
    except (GeocoderTimedOut, Exception) as e:
        print(f"Geocoding error: {str(e)}")
        return {
            "city": "Unknown",
            "state_province": None,
            "country": None,
            "country_code": None,
            "postal_code": None,
            "formatted_address": None,
        }


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
        # Get detailed location information from coordinates
        location_details = get_location_details(payload.lat, payload.lon)

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
            city=location_details["city"],
            state_province=location_details["state_province"],
            country=location_details["country"],
            country_code=location_details["country_code"],
            postal_code=location_details["postal_code"],
            formatted_address=location_details["formatted_address"],
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
            # 1. City/State/Country has changed, or
            # 2. No weather check in the last hour, or
            # 3. No previous weather check at all
            location_changed = (
                last_location.city != location_track.city
                or last_location.state_province != location_track.state_province
                or last_location.country != location_track.country
            )
            should_update_weather = (
                location_changed
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
                    # Use full location name for weather lookup
                    location_name = (
                        f"{location_track.city}, {location_track.state_province}, {location_track.country_code}"
                        if all([location_track.city, location_track.state_province, location_track.country_code])
                        else location_track.city
                    )

                    # Fetch weather data
                    await post_all_weather_data(location=location_name, client=client, db=db)

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
