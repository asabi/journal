from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CalendarEventBase(BaseModel):
    event_id: str
    calendar_id: str
    account_email: str
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    response_status: str
    attendees_count: int
    organizer_email: str
    is_recurring: bool = False
    recurring_event_id: Optional[str] = None
    conference_link: Optional[str] = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
