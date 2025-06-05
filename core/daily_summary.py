import json
import logging
import httpx
import pytz
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from core.db import (
    CalendarEvent,
    FoodImage,
    FoodLog,
    HeartRate,
    Steps,
    SleepAnalysis,
    ActiveEnergy,
    AppleExerciseTime,
    RestingHeartRate,
    HealthData,
    WeatherData,
    LocationTrack,
)
from core.config import settings
from core.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class DailySummaryService:
    def __init__(self):
        # Use dedicated summary model settings
        self.summary_model = settings.SUMMARY_OLLAMA_MODEL
        self.summary_url = settings.SUMMARY_OLLAMA_URL
        self.summary_client = httpx.Client(timeout=300.0)  # 5 minutes timeout for summaries
        self.qdrant_client = QdrantClient()
        # Set up timezone
        self.timezone = pytz.timezone(settings.TIMEZONE)

    def convert_to_local_time(self, dt_str: str) -> str:
        """Convert a datetime string from GMT to local timezone"""
        if not dt_str:
            return dt_str
        try:
            # Parse the datetime string (assuming it's in GMT)
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                # Assume UTC if no timezone info
                dt = pytz.UTC.localize(dt)
            # Convert to local timezone
            local_dt = dt.astimezone(self.timezone)
            return local_dt.isoformat()
        except:
            # Return original if conversion fails
            return dt_str

    def get_daily_data(self, db: Session, target_date: date) -> Dict[str, Any]:
        """Collect all data for a specific date using timezone-aware boundaries"""
        # Convert local date to timezone-aware datetime boundaries
        local_start = self.timezone.localize(datetime.combine(target_date, datetime.min.time()))
        local_end = self.timezone.localize(datetime.combine(target_date + timedelta(days=1), datetime.min.time()))

        # Convert to GMT for database queries (since data is stored in GMT)
        start_datetime_gmt = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
        end_datetime_gmt = local_end.astimezone(pytz.UTC).replace(tzinfo=None)

        logger.info(f"Retrieving data for {target_date} (local) = {start_datetime_gmt} to {end_datetime_gmt} (GMT)")

        data = {
            "date": target_date.isoformat(),
            "calendar_events": [],
            "calendar_locations": [],
            "food_intake": [],
            "health_metrics": {},
            "sleep_data": None,
            "exercise_data": {},
            "weather_data": [],
            "location_data": [],
        }

        # Calendar Events
        events = (
            db.query(CalendarEvent)
            .filter(and_(CalendarEvent.start_time >= start_datetime_gmt, CalendarEvent.start_time < end_datetime_gmt))
            .all()
        )

        data["calendar_events"] = [
            {
                "summary": event.summary,
                "description": event.description,
                "start_time": self.convert_to_local_time(event.start_time.isoformat()) if event.start_time else None,
                "end_time": self.convert_to_local_time(event.end_time.isoformat()) if event.end_time else None,
                "location": event.location,
                "attendees_count": event.attendees_count,
                "response_status": event.response_status,
            }
            for event in events
        ]

        # Extract unique calendar event locations for context
        calendar_locations = []
        for event in events:
            if event.location and event.location.strip():
                calendar_locations.append(
                    {
                        "location": event.location,
                        "event_summary": event.summary,
                        "start_time": (
                            self.convert_to_local_time(event.start_time.isoformat()) if event.start_time else None
                        ),
                    }
                )

        data["calendar_locations"] = calendar_locations

        # Food Intake
        food_images = (
            db.query(FoodImage)
            .filter(and_(FoodImage.timestamp >= start_datetime_gmt, FoodImage.timestamp < end_datetime_gmt))
            .all()
        )

        total_calories = 0
        meals_by_type = {}

        for image in food_images:
            for food_log in image.food_items:
                if food_log.calories:
                    total_calories += food_log.calories

                meal_type = food_log.meal_type or "unknown"
                if meal_type not in meals_by_type:
                    meals_by_type[meal_type] = []

                meals_by_type[meal_type].append(
                    {
                        "food_name": food_log.food_name,
                        "portion_size": food_log.portion_size,
                        "calories": food_log.calories,
                        "confidence": food_log.confidence,
                    }
                )

        data["food_intake"] = {
            "total_calories": total_calories,
            "meals_by_type": meals_by_type,
            "meal_count": len(food_images),
        }

        # Health Metrics
        # Steps
        steps_data = (
            db.query(Steps)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if steps_data:
            data["health_metrics"]["steps"] = steps_data.value

        # Heart Rate
        hr_data = (
            db.query(HeartRate)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if hr_data:
            data["health_metrics"]["heart_rate"] = {"avg": hr_data.avg, "min": hr_data.min, "max": hr_data.max}

        # Resting Heart Rate
        rhr_data = (
            db.query(RestingHeartRate)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if rhr_data:
            data["health_metrics"]["resting_heart_rate"] = rhr_data.value

        # Active Energy
        energy_data = (
            db.query(ActiveEnergy)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if energy_data:
            data["health_metrics"]["active_energy"] = energy_data.value

        # Exercise Time
        exercise_data = (
            db.query(AppleExerciseTime)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if exercise_data:
            data["exercise_data"]["exercise_minutes"] = exercise_data.value

        # Sleep Analysis
        sleep_data = (
            db.query(SleepAnalysis)
            .join(HealthData)
            .filter(and_(HealthData.timestamp >= start_datetime_gmt, HealthData.timestamp < end_datetime_gmt))
            .first()
        )
        if sleep_data:
            data["sleep_data"] = {
                "total_sleep": sleep_data.asleep,
                "deep_sleep": sleep_data.deep,
                "rem_sleep": sleep_data.rem,
                "core_sleep": sleep_data.core,
                "awake_time": sleep_data.awake,
                "in_bed_time": sleep_data.inBed,
                "sleep_start": (
                    self.convert_to_local_time(sleep_data.sleepStart.isoformat()) if sleep_data.sleepStart else None
                ),
                "sleep_end": (
                    self.convert_to_local_time(sleep_data.sleepEnd.isoformat()) if sleep_data.sleepEnd else None
                ),
            }
        else:
            # Explicitly set to None when no sleep data is available
            data["sleep_data"] = None

        # Weather Data - get weather records from the target date
        weather_records = (
            db.query(WeatherData)
            .filter(
                WeatherData.last_updated_epoch.between(
                    int(start_datetime_gmt.timestamp()), int(end_datetime_gmt.timestamp())
                )
            )
            .all()
        )

        for weather in weather_records:
            data["weather_data"].append(
                {
                    "location": weather.location_name,
                    "temperature_c": weather.temp_c,
                    "temperature_f": weather.temp_f,
                    "condition": weather.condition_text,
                    "humidity": weather.humidity,
                    "wind_kph": weather.wind_kph,
                    "wind_dir": weather.wind_dir,
                    "feels_like_c": weather.feelslike_c,
                    "uv_index": weather.uv,
                    "last_updated": weather.last_updated,
                }
            )

        # Location Data - get location tracks from the target date
        location_records = (
            db.query(LocationTrack)
            .filter(and_(LocationTrack.timestamp >= start_datetime_gmt, LocationTrack.timestamp < end_datetime_gmt))
            .order_by(LocationTrack.timestamp)
            .all()
        )

        # Group locations by city to avoid repetition
        unique_locations = {}
        for location in location_records:
            location_key = f"{location.city}, {location.state_province}" if location.state_province else location.city
            if location_key not in unique_locations:
                unique_locations[location_key] = {
                    "city": location.city,
                    "state_province": location.state_province,
                    "country": location.country,
                    "country_code": location.country_code,
                    "first_seen": self.convert_to_local_time(location.timestamp.isoformat()),
                    "lat": location.lat,
                    "lon": location.lon,
                }

        data["location_data"] = list(unique_locations.values())

        return data

    def generate_summary(self, daily_data: Dict[str, Any]) -> str:
        """Generate a comprehensive daily summary using Ollama"""

        # Create a structured prompt for the AI
        prompt = f"""
        Analyze the following daily data and create a comprehensive summary for {daily_data['date']}. 
        Focus on patterns, insights, and notable events. Be concise but informative.

        NOTE: All timestamps in the data below are in local timezone ({settings.TIMEZONE}).

        CRITICAL INSTRUCTIONS:
        - When data shows null/None values, this means NO DATA WAS COLLECTED for that day
        - DO NOT treat missing data as health concerns or problems
        - DO NOT mention missing data as something to be concerned about
        - Instead, focus ONLY on the data that IS available
        - If most data is missing, frame it as "a day with limited tracking" rather than problematic
        - Only mention actual zero values (when data was collected but showed 0) as potential areas of interest

        Examples:
        - If sleep_data is null: DON'T mention sleep at all, or briefly note "No sleep data was recorded for this day"
        - If steps is null: DON'T mention steps, or briefly note "Step tracking was not available"
        - If total_calories is 0 AND food data exists: This might be worth noting
        - If total_calories is 0 AND no food data exists: This just means no food was tracked

        CALENDAR EVENTS ({len(daily_data['calendar_events'])} events):
        {json.dumps(daily_data['calendar_events'], indent=2)}

        CALENDAR LOCATIONS:
        {json.dumps(daily_data['calendar_locations'], indent=2)}

        FOOD INTAKE:
        Total Calories: {daily_data['food_intake']['total_calories']}
        Meals: {json.dumps(daily_data['food_intake']['meals_by_type'], indent=2)}

        HEALTH METRICS:
        {json.dumps(daily_data['health_metrics'], indent=2)}

        EXERCISE DATA:
        {json.dumps(daily_data['exercise_data'], indent=2)}

        SLEEP DATA:
        {json.dumps(daily_data['sleep_data'], indent=2)}

        WEATHER DATA:
        {json.dumps(daily_data['weather_data'], indent=2)}

        LOCATION DATA:
        {json.dumps(daily_data['location_data'], indent=2)}

        Please provide a summary that includes:
        1. Overall day assessment based on AVAILABLE data
        2. Key activities and meetings (if any)
        3. Weather conditions and how they might have influenced the day
        4. Locations visited and any travel patterns
        5. Health and wellness highlights (only actual recorded data)
        6. Food intake patterns (only if food was tracked)
        7. Sleep quality assessment (only if sleep data exists)
        8. Notable patterns based on actual data

        Keep the summary under 500 words, personal, and insightful.
        Focus on what DID happen rather than what data is missing.
        Frame days with limited data as "quiet tracking days" rather than problematic.
        """

        try:
            response = self.summary_client.post(
                f"{self.summary_url}/api/generate",
                json={"model": self.summary_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Unable to generate summary")

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary for {daily_data['date']}: {str(e)}"

    async def create_daily_summary(self, db: Session, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Create and store a daily summary"""
        if target_date is None:
            target_date = date.today() - timedelta(days=1)  # Default to yesterday

        try:
            # Collect daily data
            daily_data = self.get_daily_data(db, target_date)

            # Generate summary
            summary = self.generate_summary(daily_data)

            # Prepare metadata for vector storage
            metadata = {
                "total_calories": daily_data["food_intake"]["total_calories"],
                "event_count": len(daily_data["calendar_events"]),
                "meal_count": daily_data["food_intake"]["meal_count"],
                "steps": daily_data["health_metrics"].get("steps"),
                "exercise_minutes": daily_data["exercise_data"].get("exercise_minutes"),
                "sleep_hours": (
                    daily_data["sleep_data"]["total_sleep"]
                    if daily_data["sleep_data"] and daily_data["sleep_data"].get("total_sleep") is not None
                    else None
                ),
                "day_of_week": target_date.strftime("%A"),
            }

            if metadata["sleep_hours"] == 0:
                metadata["sleep_hours"] = None

            # Store in vector database
            self.qdrant_client.store_daily_summary(date=target_date.isoformat(), summary=summary, metadata=metadata)

            return {"date": target_date.isoformat(), "summary": summary, "metadata": metadata, "raw_data": daily_data}

        except Exception as e:
            logger.error(f"Error creating daily summary: {e}")
            raise

    async def query_summaries(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Query daily summaries using natural language"""
        try:
            # Search vector database
            search_results = self.qdrant_client.search_summaries(query, limit)

            # Format results for response
            results = []
            for result in search_results:
                payload = result.get("payload", {})
                results.append(
                    {
                        "date": payload.get("date"),
                        "summary": payload.get("summary"),
                        "score": result.get("score"),
                        "metadata": {k: v for k, v in payload.items() if k not in ["date", "summary", "created_at"]},
                    }
                )

            # Generate an AI response based on the search results
            context = "\n\n".join(
                [f"Date: {r['date']}\nSummary: {r['summary']}" for r in results[:3]]  # Use top 3 results for context
            )

            ai_prompt = f"""
            Based on the following daily summaries, answer this question: "{query}"
            
            Relevant daily summaries:
            {context}
            
            Provide a comprehensive answer based on the patterns and information in these summaries.
            If you can identify trends or patterns, mention them. Be specific and cite dates when relevant.
            """

            ai_response = self.summary_client.post(
                f"{self.summary_url}/api/generate",
                json={"model": self.summary_model, "prompt": ai_prompt, "stream": False},
            )
            ai_response.raise_for_status()
            ai_result = ai_response.json()

            return {
                "query": query,
                "ai_response": ai_result.get("response", "Unable to generate response"),
                "relevant_summaries": results,
                "total_found": len(search_results),
            }

        except Exception as e:
            logger.error(f"Error querying summaries: {e}")
            raise
