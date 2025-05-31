from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apis.weather.routes import router as weather_router
from apis.locations.routes import router as locations_router
from apis.health.routes import router as health_router
from apis.calendar import routes as calendar_routes
from apis.sheets.routes import router as sheets_router
from core.db import Base, engine
from core.security import get_api_key


app = FastAPI(title="Life Journal API", version="0.1.0")

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefixes and API key dependency
app.include_router(weather_router, prefix="/weather", tags=["Weather"], dependencies=[Depends(get_api_key)])
app.include_router(locations_router, prefix="/locations", tags=["Location"], dependencies=[Depends(get_api_key)])
app.include_router(health_router, prefix="/health", tags=["Health"], dependencies=[Depends(get_api_key)])
app.include_router(calendar_routes.router, prefix="/calendar", tags=["Calendar"], dependencies=[Depends(get_api_key)])
app.include_router(sheets_router, prefix="/sheets", tags=["Sheets"], dependencies=[Depends(get_api_key)])


@app.get("/")
async def read_root():
    return {
        "message": "Life Journal API",
        "available_endpoints": ["/weather", "/google", "/locations", "/health", "/calendar", "/sheets"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
