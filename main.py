from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.weather.routes import router as weather_router
from apis.google.routes import router as google_router
from apis.locations.routes import router as locations_router
from apis.health.routes import router as health_router
from core.db import Base, engine


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

# Include routers with prefixes
app.include_router(weather_router, prefix="/weather")
app.include_router(google_router, prefix="/google")
app.include_router(locations_router, prefix="/locations")
app.include_router(health_router, prefix="/health")


@app.get("/")
def read_root():
    return {"message": "Life Journal API", "available_endpoints": ["/weather", "/google", "/locations", "/health"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
