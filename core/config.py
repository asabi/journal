from pydantic_settings import BaseSettings
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = ""
    PROJECT_NAME: str = "Life Journal API"
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")

    class Config:
        case_sensitive = True


settings = Settings()
