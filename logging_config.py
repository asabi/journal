import logging
import os

# Create a logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/health_api.log",
    filemode="a",  # Append to the log file
)

logger = logging.getLogger(__name__)
