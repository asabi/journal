from pydantic_settings import BaseSettings
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = ""
    PROJECT_NAME: str = "Life Journal API"
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./health.db")

    class Config:
        case_sensitive = True


settings = Settings()
