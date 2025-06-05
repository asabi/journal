from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.db import get_db
from core.daily_summary import DailySummaryService
from datetime import date, datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
summary_service = DailySummaryService()


@router.post("/create")
async def create_daily_summary(
    target_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to yesterday."),
    db: Session = Depends(get_db),
):
    """
    Create a daily summary for the specified date (or yesterday if not specified).
    Collects all data from calendar events, food intake, health metrics, and sleep data.
    Generates an AI summary and stores it in the vector database.
    """
    try:
        # Parse target date
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        else:
            parsed_date = None  # Will default to yesterday in the service

        # Create summary
        result = await summary_service.create_daily_summary(db, parsed_date)

        return {
            "message": "Daily summary created successfully",
            "date": result["date"],
            "summary": result["summary"],
            "metadata": result["metadata"],
        }

    except Exception as e:
        logger.error(f"Error creating daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
async def query_summaries(
    q: str = Query(..., description="Natural language query about your daily patterns"),
    limit: int = Query(5, description="Maximum number of relevant summaries to consider", ge=1, le=20),
):
    """
    Query your daily summaries using natural language.

    Examples:
    - "What kind of days are most stressful for me?"
    - "What days of the week do I have the most interviews?"
    - "When do I sleep the best?"
    - "What are my most productive days like?"
    - "How does my exercise affect my sleep?"
    """
    try:
        result = await summary_service.query_summaries(q, limit)

        return {
            "query": result["query"],
            "answer": result["ai_response"],
            "relevant_summaries": result["relevant_summaries"],
            "total_found": result["total_found"],
        }

    except Exception as e:
        logger.error(f"Error querying summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_summaries(
    limit: int = Query(7, description="Number of recent summaries to retrieve", ge=1, le=30),
):
    """
    Get recent daily summaries without querying.
    Useful for reviewing recent days or getting an overview.
    """
    try:
        # Use a broad query to get recent summaries
        result = await summary_service.query_summaries("recent daily activities", limit)

        # Sort by date (most recent first)
        summaries = sorted(result["relevant_summaries"], key=lambda x: x["date"], reverse=True)

        return {"summaries": summaries[:limit], "total_found": len(summaries)}

    except Exception as e:
        logger.error(f"Error getting recent summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-create")
async def create_bulk_summaries(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """
    Create daily summaries for a range of dates.
    Useful for backfilling summaries or processing multiple days at once.
    """
    try:
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        if start > end:
            raise HTTPException(status_code=400, detail="Start date must be before or equal to end date.")

        # Limit the range to prevent abuse
        if (end - start).days > 30:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 30 days.")

        results = []
        current_date = start

        while current_date <= end:
            try:
                result = await summary_service.create_daily_summary(db, current_date)
                results.append({"date": result["date"], "status": "success", "summary_length": len(result["summary"])})
            except Exception as e:
                logger.error(f"Error creating summary for {current_date}: {e}")
                results.append({"date": current_date.isoformat(), "status": "error", "error": str(e)})

            current_date += timedelta(days=1)

        successful = len([r for r in results if r["status"] == "success"])
        failed = len([r for r in results if r["status"] == "error"])

        return {
            "message": f"Bulk summary creation completed. {successful} successful, {failed} failed.",
            "results": results,
            "summary": {"total_processed": len(results), "successful": successful, "failed": failed},
        }

    except Exception as e:
        logger.error(f"Error in bulk summary creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
