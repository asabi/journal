#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source the .env file if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    # Export all variables from .env file, excluding comments and section headers
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | grep -v '^\[.*\]' | xargs)
else
    echo "Error: .env file not found in $SCRIPT_DIR"
    exit 1
fi

# Check if API_KEY is set
if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY not found in .env file"
    exit 1
fi

# Get current date for logging
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to make API calls and log results
make_api_call() {
    local endpoint=$1
    local data=$2
    local method=${3:-GET}
    
    response=$(curl -s -X "$method" \
        -H "x-api-key: $API_KEY" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} \
        "http://localhost:8000$endpoint")
    
    echo "[$CURRENT_DATE] Called $endpoint: $response"
}

# Sync calendar events
echo "[$CURRENT_DATE] Starting daily sync..."
make_api_call "/calendar/sync-today" "" "POST"

# Get weather for Richmond, BC
make_api_call "/weather/all?location=Richmond,BC" "" "POST"

# Sync weekly reflections
make_api_call "/sheets/sync-reflections" "" "POST"

echo "[$CURRENT_DATE] Daily sync completed" 