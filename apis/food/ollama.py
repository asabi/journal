import httpx
import base64
from typing import Dict, List, Optional
import logging
import json
from core.config import settings

logger = logging.getLogger(__name__)


class OllamaAPI:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.client = httpx.Client(timeout=120.0)  # Increased timeout to 120 seconds for image processing
        self.model = settings.OLLAMA_MODEL

    def analyze_food_image(self, image_data: bytes) -> Dict:
        """
        Analyze a food image using Ollama and return detected foods with portions and calories.

        Args:
            image_data: Raw image bytes

        Returns:
            Dict containing analyzed foods, portions, and estimated calories
        """
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Construct the prompt
        prompt = """
        Analyze this food image and provide a detailed breakdown in JSON format. Include:
        1. Each distinct food item visible
        2. Estimated portion size for each item
        3. Estimated calories for each item (total for the portion size)
        4. Your confidence level for each detection (0-1)

        Format your response as valid JSON like this:
        {
            "foods": [
                {
                    "name": "food name",
                    "portion": "portion size",
                    "calories": estimated_calories,
                    "confidence": confidence_level
                },
                ...
            ],
            "total_calories": sum_of_all_calories
        }

        Be specific about portion sizes (e.g., "1 cup", "200g", "1 medium piece").
        If you're unsure about a food item, include it with lower confidence.
        """

        try:
            # Make request to Ollama
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "images": [base64_image], "stream": False},
            )
            response.raise_for_status()

            # Extract the response
            result = response.json()
            response_text = result.get("response", "")

            # Try to find and parse the JSON part of the response
            try:
                # Look for JSON-like structure in the response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("No JSON structure found in response")

                # Validate the structure
                if not isinstance(analysis, dict) or "foods" not in analysis:
                    raise ValueError("Invalid response structure")

                return analysis

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                logger.debug(f"Raw response: {response_text}")
                raise ValueError("Failed to parse AI response")

        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise
