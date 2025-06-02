from pydantic_settings import BaseSettings
import dotenv
import os
from typing import List, Dict, Optional
from pydantic import Field

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
    WEEKLY_REFLECTIONS_SPREADSHEET_ID: str = os.getenv(
        "WEEKLY_REFLECTIONS_SPREADSHEET_ID", ""
    )  # Google Sheet ID for weekly reflections

    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field("us-east-1", env="AWS_REGION")
    AWS_BUCKET_NAME: str = Field("daily_food_images", env="AWS_BUCKET_NAME")

    # Ollama Settings
    OLLAMA_MODEL: str = Field("llava", env="OLLAMA_MODEL")  # Default to llava if not specified
    OLLAMA_URL: str = Field("http://100.119.144.30:11434", env="OLLAMA_URL")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
