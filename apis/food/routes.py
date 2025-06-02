from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from core.db import get_db, FoodImage, FoodLog
from core.s3 import S3Handler
from .ollama import OllamaAPI
from datetime import datetime, time
from typing import List, Optional
import json

router = APIRouter()
ollama_api = OllamaAPI()
s3_handler = S3Handler()


def determine_meal_type(current_time: time) -> str:
    """
    Determine meal type based on time of day:
    - Breakfast: 5:00 AM - 10:59 AM
    - Brunch: 11:00 AM - 11:59 AM
    - Lunch: 12:00 PM - 3:59 PM
    - Snack: 4:00 PM - 4:59 PM
    - Dinner: 5:00 PM - 9:59 PM
    - Late Snack: 08:00 PM - 4:59 AM
    """
    if time(5, 0) <= current_time < time(11, 0):
        return "breakfast"
    elif time(11, 0) <= current_time < time(12, 0):
        return "brunch"
    elif time(12, 0) <= current_time < time(16, 0):
        return "lunch"
    elif time(16, 0) <= current_time < time(17, 0):
        return "snack"
    elif time(17, 0) <= current_time < time(20, 0):
        return "dinner"
    else:  # Between 10 PM and 5 AM
        return "late_snack"


@router.post("/analyze")
async def analyze_food(
    image: UploadFile = File(...),
    meal_type: Optional[str] = Query(None, description="Type of meal (breakfast, lunch, dinner, snack)"),
    db: Session = Depends(get_db),
):
    """
    Analyze a food image and return calorie estimates.
    Uploads the image to S3 and stores analysis results in the database.
    """
    try:
        # If meal_type is not provided, determine it based on current time
        if not meal_type:
            current_time = datetime.now().time()
            meal_type = determine_meal_type(current_time)

        # Read image data
        image_data = await image.read()

        # Upload to S3
        s3_location = await s3_handler.upload_image(image_data, image.filename)

        # Analyze image with Ollama
        analysis = ollama_api.analyze_food_image(image_data)

        # Create database entry for the image
        food_image = FoodImage(
            timestamp=datetime.utcnow(),
            s3_bucket=s3_location["bucket"],
            s3_region=s3_location["region"],
            s3_key=s3_location["key"],
            raw_analysis=json.dumps(analysis),
        )
        db.add(food_image)
        db.flush()  # Get the ID without committing

        # Add individual food items
        total_calories = 0
        food_items = []
        food_items_string = ""
        for food in analysis.get("foods", []):
            food_log = FoodLog(
                image_id=food_image.id,
                food_name=food["name"],
                portion_size=food["portion"],
                calories=food["calories"],
                confidence=food["confidence"],
                meal_type=meal_type,
            )
            food_items_string += f"{food['name']} - {food['portion']}\n"
            db.add(food_log)
            total_calories += food["calories"]
            food_items.append(food)

        db.commit()

        # Generate a presigned URL for the image
        image_url = s3_handler.get_image_url(s3_location["key"])

        # Prepare response
        # return the total calories and the food items as a string
        return f"Total calories: {total_calories}\nFood items: {food_items_string}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def list_entries(
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
):
    """
    List recent food entries with their analysis results.
    Optionally filter by meal type.
    """
    # Base query
    query = db.query(FoodImage).order_by(FoodImage.timestamp.desc())

    # Apply meal type filter if provided
    if meal_type:
        query = query.join(FoodLog).filter(FoodLog.meal_type == meal_type)

    # Apply pagination
    images = query.offset(offset).limit(limit).all()

    return [
        {
            "id": image.id,
            "timestamp": image.timestamp,
            "image_url": s3_handler.get_image_url(image.s3_key),
            "foods": [
                {
                    "name": item.food_name,
                    "portion": item.portion_size,
                    "calories": item.calories,
                    "confidence": item.confidence,
                    "meal_type": item.meal_type,
                }
                for item in image.food_items
            ],
            "total_calories": sum(item.calories for item in image.food_items if item.calories),
        }
        for image in images
    ]


@router.get("/entries/{image_id}")
async def get_entry(image_id: int, db: Session = Depends(get_db)):
    """
    Get details for a specific food entry.
    """
    image = db.query(FoodImage).filter(FoodImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Food entry not found")

    return {
        "id": image.id,
        "timestamp": image.timestamp,
        "image_url": s3_handler.get_image_url(image.s3_key),
        "foods": [
            {
                "name": item.food_name,
                "portion": item.portion_size,
                "calories": item.calories,
                "confidence": item.confidence,
                "meal_type": item.meal_type,
            }
            for item in image.food_items
        ],
        "total_calories": sum(item.calories for item in image.food_items if item.calories),
        "raw_analysis": json.loads(image.raw_analysis) if image.raw_analysis else None,
    }
