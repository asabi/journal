from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db, WeeklyReflection
from core.config import settings
from .google_sheets import GoogleSheetsAPI
from apis.calendar.routes import get_calendar_configs
from datetime import datetime
from typing import List, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sync-reflections")
async def sync_reflections(db: Session = Depends(get_db)):
    """
    Sync weekly reflections from Google Sheets.
    Uses the spreadsheet ID from environment settings.
    """
    if not settings.WEEKLY_REFLECTIONS_SPREADSHEET_ID:
        raise HTTPException(
            status_code=400, detail="WEEKLY_REFLECTIONS_SPREADSHEET_ID not configured in environment settings"
        )

    calendar_configs = get_calendar_configs()  # Reuse calendar configs since we're using the same credentials
    sync_results = {}
    errors = []
    total_synced = 0

    for account_config in calendar_configs:
        try:
            sheets_api = GoogleSheetsAPI(account_config)
            reflections = sheets_api.get_weekly_reflections(settings.WEEKLY_REFLECTIONS_SPREADSHEET_ID)

            synced_count = 0
            for reflection_data in reflections:
                try:
                    # Check if reflection already exists
                    existing_reflection = (
                        db.query(WeeklyReflection)
                        .filter_by(email=reflection_data["email"], timestamp=reflection_data["timestamp"])
                        .first()
                    )

                    if existing_reflection:
                        # Update existing reflection
                        for key, value in reflection_data.items():
                            setattr(existing_reflection, key, value)
                    else:
                        # Create new reflection
                        new_reflection = WeeklyReflection(**reflection_data)
                        db.add(new_reflection)

                    synced_count += 1

                except Exception as e:
                    errors.append(f"Error processing reflection for {reflection_data.get('email')}: {str(e)}")
                    continue

            db.commit()
            sync_results[account_config["email"]] = {"reflections_synced": synced_count}
            total_synced += synced_count

        except Exception as e:
            error_str = str(e)
            # Check if error is due to insufficient permissions or API not enabled
            if (
                "insufficient authentication scopes" in error_str.lower()
                or "request had insufficient authentication" in error_str.lower()
                or "sheets api has not been used" in error_str.lower()
            ):
                logger.info(f"Skipping {account_config['email']}: No Sheets access or API not enabled")
                continue
            else:
                errors.append(f"Error syncing reflections for {account_config['email']}: {error_str}")
                continue

    response = {
        "message": "Weekly reflections sync completed",
        "sync_results": sync_results,
        "total_reflections_synced": total_synced,
        "accounts_processed": len(sync_results),
    }

    if errors:
        response["errors"] = errors

    return response
