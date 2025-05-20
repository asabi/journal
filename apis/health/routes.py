from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_health_data():
    return {"message": "Health data endpoint - not implemented yet"}

@router.get("/activity")
def get_activity_summary():
    return {"message": "Activity summary endpoint - not implemented yet"}
