from pydantic import BaseModel
from typing import List, Optional


class WeatherDataSchema(BaseModel):
    location_name: str
    location_region: str
    location_country: str
    location_lat: float
    location_lon: float
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    condition_text: str
    condition_icon: str
    condition_code: int
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: int
    pressure_in: int
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    vis_km: int
    vis_miles: int
    uv: int
    gust_mph: float
    gust_kph: float

    class Config:
        from_attributes = True


class WeatherAlertSchema(BaseModel):
    location_name: str
    headline: Optional[str] = None
    severity: Optional[str] = None
    urgency: Optional[str] = None
    areas: Optional[str] = None
    category: Optional[str] = None
    certainty: Optional[str] = None
    event: Optional[str] = None
    note: Optional[str] = None
    effective: Optional[str] = None
    expires: Optional[str] = None
    desc: Optional[str] = None
    instruction: Optional[str] = None

    class Config:
        from_attributes = True


class AirQualitySchema(BaseModel):
    location_name: str
    last_updated: str
    co: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    us_epa_index: Optional[int] = None
    gb_defra_index: Optional[int] = None

    class Config:
        from_attributes = True


class MarineWeatherSchema(BaseModel):
    location_name: str
    last_updated: str
    tide_time: Optional[str] = None
    tide_height_mt: Optional[float] = None
    tide_type: Optional[str] = None
    swell_height_m: Optional[float] = None
    swell_direction: Optional[str] = None
    swell_direction_degrees: Optional[int] = None
    swell_period_seconds: Optional[int] = None
    water_temp_c: Optional[float] = None
    water_temp_f: Optional[float] = None

    class Config:
        from_attributes = True


class AstronomyDataSchema(BaseModel):
    location_name: str
    date: Optional[str] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    moonrise: Optional[str] = None
    moonset: Optional[str] = None
    moon_phase: Optional[str] = None
    moon_illumination: Optional[int] = None
    is_moon_up: Optional[int] = None
    is_sun_up: Optional[int] = None

    class Config:
        from_attributes = True


class AllWeatherDataResponse(BaseModel):
    current_weather: Optional[WeatherDataSchema] = None
    alerts: Optional[List[WeatherAlertSchema]] = None
    air_quality: Optional[AirQualitySchema] = None
    marine: Optional[List[MarineWeatherSchema]] = None
    astronomy: Optional[AstronomyDataSchema] = None
