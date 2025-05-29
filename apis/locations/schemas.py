from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OwnTracksPayload(BaseModel):
    """Schema for OwnTracks HTTP mode payload"""

    _type: str
    tid: Optional[str] = None
    lat: float
    lon: float
    alt: Optional[float] = None
    acc: Optional[float] = None
    batt: Optional[int] = None
    vel: Optional[float] = None
    t: Optional[str] = None  # Trigger
    tst: Optional[int] = None  # Unix timestamp


class LocationTrackResponse(BaseModel):
    """Response schema for location tracking"""

    id: int
    timestamp: datetime
    lat: float
    lon: float
    alt: Optional[float] = None
    acc: Optional[float] = None
    batt: Optional[int] = None
    vel: Optional[float] = None
    tid: Optional[str] = None
    city: str
    last_weather_check: Optional[datetime] = None

    class Config:
        from_attributes = True
