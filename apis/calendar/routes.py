# apis/calendar/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db, CalendarEvent
from datetime import datetime, date
from typing import List, Dict
from .google_calendar import GoogleCalendarAPI
from .schemas import CalendarEventResponse
from core.config import settings
import os

router = APIRouter()


def get_calendar_configs():
    """Get calendar configurations from settings"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return [
        {
            "email": email,
            "credentials_file": os.path.join(base_dir, "google_creds", f"{email.split('@')[0]}_credentials.json"),
            "token_file": os.path.join(base_dir, "google_creds", f"{email.split('@')[0]}_token.pickle"),
        }
        for email in settings.GOOGLE_CALENDAR_EMAILS
    ]


@router.get("/calendars")
async def list_calendars():
    """List all available calendars for configured accounts"""
    calendar_configs = get_calendar_configs()
    calendars_by_account = {}
    errors = []

    for account_config in calendar_configs:
        try:
            calendar_api = GoogleCalendarAPI(account_config)
            calendars = calendar_api.list_calendars()
            calendars_by_account[account_config["email"]] = {
                "calendars": calendars,
                "total_calendars": len(calendars),
                "primary_calendar": next((cal for cal in calendars if cal.get("primary")), None),
            }
        except Exception as e:
            errors.append(f"Error listing calendars for {account_config['email']}: {str(e)}")
            continue

    response = {
        "accounts": calendars_by_account,
        "total_accounts": len(calendars_by_account),
        "total_calendars": sum(acc["total_calendars"] for acc in calendars_by_account.values()),
    }

    if errors:
        response["errors"] = errors

    return response


@router.post("/sync-today")
async def sync_today_events(db: Session = Depends(get_db)):
    """
    Sync calendar events for today from all configured Google accounts.
    Designed to be called by a scheduled task at 11 PM.
    """
    today = date.today()
    calendar_configs = get_calendar_configs()

    sync_results = {}
    errors = []

    for account_config in calendar_configs:
        try:
            calendar_api = GoogleCalendarAPI(account_config)
            events = calendar_api.get_events_for_day(today, allowed_calendar_ids=settings.ALLOWED_CALENDAR_IDS)

            # Track events per calendar for this account
            events_by_calendar = {}
            for event in events:
                cal_id = event["calendar_id"]
                if cal_id not in events_by_calendar:
                    events_by_calendar[cal_id] = 0
                events_by_calendar[cal_id] += 1

            # Store events in database
            for event_data in events:
                try:
                    existing_event = (
                        db.query(CalendarEvent)
                        .filter_by(event_id=event_data["event_id"], calendar_id=event_data["calendar_id"])
                        .first()
                    )

                    if existing_event:
                        for key, value in event_data.items():
                            setattr(existing_event, key, value)
                    else:
                        new_event = CalendarEvent(**event_data)
                        db.add(new_event)

                except Exception as e:
                    errors.append(f"Error saving event {event_data['event_id']}: {str(e)}")
                    continue

            sync_results[account_config["email"]] = {
                "total_events": len(events),
                "events_by_calendar": events_by_calendar,
            }

        except Exception as e:
            errors.append(f"Error syncing calendar for {account_config['email']}: {str(e)}")
            continue

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    response = {
        "message": "Calendar sync completed",
        "sync_results": sync_results,
        "total_events": sum(result["total_events"] for result in sync_results.values()),
        "accounts_processed": len(sync_results),
    }

    if errors:
        response["errors"] = errors

    return response


@router.get("/events/today", response_model=List[CalendarEventResponse])
async def get_today_events(db: Session = Depends(get_db)):
    """Get all events stored for today"""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    events = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.start_time >= today_start, CalendarEvent.start_time <= today_end)
        .order_by(CalendarEvent.start_time)
        .all()
    )

    return events


@router.get("/events/{date}", response_model=List[CalendarEventResponse])
async def get_events_by_date(date_str: str, db: Session = Depends(get_db)):
    """Get all events for a specific date (format: YYYY-MM-DD)"""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    events = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.start_time >= day_start, CalendarEvent.start_time <= day_end)
        .order_by(CalendarEvent.start_time)
        .all()
    )

    return events
