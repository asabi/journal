from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete your token files.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/spreadsheets",  # Full access to sheets
]


class GoogleSheetsAPI:
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
        self.service = build("sheets", "v4", credentials=self.credentials)

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

    def get_weekly_reflections(self, spreadsheet_id: str) -> List[Dict]:
        """
        Get weekly reflections from the specified Google Sheet.
        Assumes the sheet name matches the email address.
        """
        try:
            # Get the data from the sheet
            sheet_range = f"'{self.email}'!A2:J"  # Start from row 2 to skip headers
            result = (
                self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            )

            values = result.get("values", [])
            if not values:
                logger.info("No data found in the sheet.")
                return []

            reflections = []
            for row in values:
                # Pad the row with None values if it's shorter than expected
                row_data = row + [None] * (10 - len(row))

                reflection = {
                    "timestamp": datetime.strptime(row_data[0], "%m/%d/%Y %H:%M:%S") if row_data[0] else None,
                    "proud_of": row_data[1],
                    "email": row_data[2],
                    "principles_upheld": row_data[3],
                    "learnings": row_data[4],
                    "do_differently": row_data[5],
                    "challenges": row_data[6],
                    "week_word": row_data[7],
                    "week_feeling": row_data[8],
                    "additional_notes": row_data[9],
                }
                reflections.append(reflection)

            return reflections

        except Exception as e:
            logger.error(f"Error fetching weekly reflections: {str(e)}")
            raise
