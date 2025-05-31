# apis/calendar/google_calendar.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, date, timezone
import os
import pickle
import logging
from typing import List, Dict, Optional
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarAPI:
    def __init__(self, account_config):
        """
        account_config should contain:
        - email: Google account email
        - credentials_file: Path to credentials.json
        - token_file: Path to token pickle file
        """
        self.email = account_config["email"]
        self.credentials_file = account_config["credentials_file"]
        self.token_file = account_config["token_file"]
        self.credentials = None
        self._load_credentials()
        self.service = build("calendar", "v3", credentials=self.credentials)
        self.timezone = None  # Will be set based on primary calendar

    def _load_credentials(self):
        """Load or create credentials"""
        logger.info(f"Loading credentials for {self.email}")
        logger.info(f"Credentials file: {self.credentials_file}")
        logger.info(f"Token file: {self.token_file}")

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")

        if os.path.exists(self.token_file):
            logger.info("Found existing token file")
            with open(self.token_file, "rb") as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            logger.info("Credentials need to be refreshed or created")
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing expired credentials")
                self.credentials.refresh(Request())
            else:
                logger.info("Creating new credentials through OAuth flow")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                self.credentials = flow.run_local_server(port=0)

            # Save the credentials for future use
            logger.info("Saving credentials to token file")
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            with open(self.token_file, "wb") as token:
                pickle.dump(self.credentials, token)

    def _get_calendar_timezone(self):
        """Get timezone from primary calendar"""
        if not self.timezone:
            try:
                primary_calendar = self.service.calendars().get(calendarId="primary").execute()
                self.timezone = pytz.timezone(primary_calendar.get("timeZone", "UTC"))
                logger.info(f"Using timezone: {self.timezone}")
            except Exception as e:
                logger.warning(f"Could not get calendar timezone: {e}. Using UTC.")
                self.timezone = pytz.UTC
        return self.timezone

    def list_calendars(self) -> List[Dict]:
        """List all available calendars with their details"""
        logger.info(f"Listing calendars for {self.email}")
        calendars = []
        page_token = None

        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar in calendar_list["items"]:
                calendars.append(
                    {
                        "id": calendar["id"],
                        "summary": calendar.get("summary", "No Title"),
                        "description": calendar.get("description"),
                        "primary": calendar.get("primary", False),
                        "owner": calendar.get("owner", {}).get("email"),
                        "access_role": calendar.get("accessRole"),
                        "time_zone": calendar.get("timeZone"),
                    }
                )

            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break

        logger.info(f"Found {len(calendars)} calendars")
        return calendars

    def get_events_for_day(
        self, target_date: date = None, allowed_calendar_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get all events for a specific day

        Args:
            target_date: The date to get events for (defaults to today)
            allowed_calendar_ids: List of calendar IDs to include (defaults to all calendars)
        """
        if target_date is None:
            target_date = date.today()

        logger.info(f"Getting events for {target_date} from {self.email}")

        # Get calendar's timezone
        tz = self._get_calendar_timezone()

        # Set time boundaries for the day in the calendar's timezone
        local_start = tz.localize(datetime.combine(target_date, datetime.min.time()))
        local_end = tz.localize(datetime.combine(target_date, datetime.max.time()))

        # Convert to UTC for API request
        start_time = local_start.astimezone(pytz.UTC)
        end_time = local_end.astimezone(pytz.UTC)

        logger.info(f"Fetching events between {start_time} and {end_time} ({tz})")

        # Get all calendars for the account
        logger.info("Fetching calendar list")
        all_events = []
        page_token = None

        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar in calendar_list["items"]:
                # Skip calendars not in allowed_calendar_ids if specified
                if allowed_calendar_ids and calendar["id"] not in allowed_calendar_ids:
                    logger.info(f"Skipping calendar {calendar.get('summary', 'Unknown')} (not in allowed list)")
                    continue

                logger.info(f"Fetching events from calendar: {calendar.get('summary', 'Unknown')} ({calendar['id']})")

                # Get events with pagination
                events_page_token = None
                while True:
                    events_result = (
                        self.service.events()
                        .list(
                            calendarId=calendar["id"],
                            timeMin=start_time.isoformat(),
                            timeMax=end_time.isoformat(),
                            singleEvents=True,
                            orderBy="startTime",
                            pageToken=events_page_token,
                        )
                        .execute()
                    )

                    events = events_result.get("items", [])
                    logger.info(f"Found {len(events)} events in current page")

                    for event in events:
                        try:
                            # Skip declined events
                            my_response = next(
                                (
                                    attendee["responseStatus"]
                                    for attendee in event.get("attendees", [])
                                    if attendee.get("email") == self.email
                                ),
                                event.get("responseStatus", "needsAction"),
                            )

                            if my_response != "declined":
                                event_data = {
                                    "event_id": event["id"],
                                    "calendar_id": calendar["id"],
                                    "account_email": self.email,
                                    "summary": event.get("summary", "No Title"),
                                    "description": event.get("description"),
                                    "start_time": self._parse_event_time(event["start"]),
                                    "end_time": self._parse_event_time(event["end"]),
                                    "location": event.get("location"),
                                    "response_status": my_response,
                                    "attendees_count": len(event.get("attendees", [])),
                                    "organizer_email": event.get("organizer", {}).get("email", self.email),
                                    "is_recurring": "recurringEventId" in event,
                                    "recurring_event_id": event.get("recurringEventId"),
                                    "conference_link": self._get_conference_link(event),
                                    "is_busy": event.get("transparency")
                                    != "transparent",  # If transparency is not set or is "opaque", the event is busy
                                }
                                all_events.append(event_data)
                                logger.debug(
                                    f"Added event: {event_data['summary']} ({event_data['start_time']} - {event_data['end_time']})"
                                )
                        except Exception as e:
                            logger.error(f"Error processing event {event.get('id', 'Unknown')}: {str(e)}")
                            logger.error(f"Event data: {event}")
                            continue

                    events_page_token = events_result.get("nextPageToken")
                    if not events_page_token:
                        break

            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break

        logger.info(f"Total events found for {target_date}: {len(all_events)}")
        return all_events

    def _parse_event_time(self, time_data):
        """Parse event time from Google Calendar format"""
        if "dateTime" in time_data:
            # Handle timezone-aware datetime
            dt = datetime.fromisoformat(time_data["dateTime"].replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            return dt
        else:
            # Handle all-day events
            dt = datetime.combine(datetime.strptime(time_data["date"], "%Y-%m-%d").date(), datetime.min.time())
            return self._get_calendar_timezone().localize(dt)

    def _get_conference_link(self, event):
        """Extract conference link from event"""
        if "conferenceData" in event:
            for entry in event["conferenceData"].get("entryPoints", []):
                if entry.get("entryPointType") == "video":
                    return entry.get("uri")
        return None
