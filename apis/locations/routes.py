from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_locations():
    return {"message": "Location tracking endpoint - not implemented yet"}

@router.post("/track")
def track_location():
    return {"message": "Location tracking initiated"}
