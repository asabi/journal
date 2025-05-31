from pydantic_settings import BaseSettings
import dotenv
import os
from typing import List, Dict, Optional

# Load environment variables from .env file
dotenv.load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = ""
    PROJECT_NAME: str = "Life Journal API"
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./health.db")
    API_KEY: str = os.getenv("API_KEY", "your-secret-key-here")
    GOOGLE_CALENDAR_ACCOUNTS: List[Dict[str, str]] = [
        {
            "email": "alon.sabi@quandri.io",
            "credentials_file": "/path/to/first-credentials.json",
            "token_file": "/path/to/first-token.pickle",
        },
        # {
        #     "email": "your-second-email@gmail.com",
        #     "credentials_file": "/path/to/second-credentials.json",
        #     "token_file": "/path/to/second-token.pickle",
        # },
    ]
    GOOGLE_CALENDAR_EMAILS: List[str] = []  # List of Google account emails to sync
    ALLOWED_CALENDAR_IDS: Optional[List[str]] = None  # List of calendar IDs to include (None means all calendars)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
