from pydantic import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = ""
    PROJECT_NAME: str = "Life Journal API"
    WEATHER_API_KEY: str  # Will be loaded from environment variables
    
    class Config:
        case_sensitive = True

settings = Settings()
