from pydantic import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = ""
    PROJECT_NAME: str = "Life Journal API"
    
    class Config:
        case_sensitive = True

settings = Settings()
