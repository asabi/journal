from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_google_data():
    return {"message": "Google services endpoint - not implemented yet"}

@router.get("/calendar")
def get_calendar_events():
    return {"message": "Calendar events endpoint - not implemented yet"}
