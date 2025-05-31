# Life Journal API

## Installation & Running (with Docker)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/life_journal.git
   cd life_journal
   ```

2. **Build the Docker image:**
   ```sh
   docker build -t life-journal-api .
   ```

3. **Run the Docker container:**
   ```sh
   docker run -d -p 8000:8000 --env-file .env --restart unless-stopped --name journal life-journal-api
   ```

4. **Access the API:**
   - Open your browser and go to: [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

## Google Calendar Integration Setup

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API:
     - Go to "APIs & Services" > "Library"
     - Search for "Google Calendar API"
     - Click "Enable"

2. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Give it a name (e.g., "Life Journal Calendar Integration")
   - Click "Create"
   - Download the credentials JSON file

3. **Set Up Credentials:**
   - Create a `google_creds` directory in your project root:
     ```sh
     mkdir -p google_creds
     ```
   - For each Google account you want to integrate:
     - Rename the downloaded credentials file to `{email_prefix}_credentials.json`
     - Example: for `john.doe@gmail.com`, name it `john.doe_credentials.json`
     - Place it in the `google_creds` directory

4. **Update Environment Variables:**
   Add the following to your `.env` file:
   ```
   # API Authentication
   API_KEY=your-secret-key-here

   # Google Calendar Integration
   GOOGLE_CALENDAR_EMAILS=["your.email@gmail.com"]  # List of emails to sync
   ALLOWED_CALENDAR_IDS=["your.email@gmail.com"]    # Optional: specific calendar IDs to sync
   ```

5. **Install Required Packages:**
   ```sh
   pip install google-auth-oauthlib google-api-python-client
   ```

6. **First-Time Setup:**
   
   a. List available calendars:
   ```sh
   curl -H "X-API-Key: your_secret_api_key_here" http://localhost:8000/calendar/calendars
   ```
   This will open a browser window for OAuth authentication. Follow the prompts to authorize the application.

   Example response:
   ```json
   {
     "accounts": {
       "john.doe@gmail.com": {
         "calendars": [
           {
             "id": "john.doe@gmail.com",
             "summary": "My Calendar",
             "description": null,
             "primary": true,
             "owner": "john.doe@gmail.com",
             "access_role": "owner",
             "time_zone": "America/Los_Angeles"
           },
           {
             "id": "family@group.calendar.google.com",
             "summary": "Family Calendar",
             "description": "Shared family calendar",
             "primary": false,
             "owner": "john.doe@gmail.com",
             "access_role": "owner",
             "time_zone": "America/Los_Angeles"
           }
         ],
         "total_calendars": 2,
         "primary_calendar": {
           "id": "john.doe@gmail.com",
           "summary": "My Calendar",
           "primary": true
         }
       },
       "jane.doe@gmail.com": {
         "calendars": [
           // ... similar structure for second account
         ],
         "total_calendars": 3,
         "primary_calendar": {
           // ... primary calendar info
         }
       }
     },
     "total_accounts": 2,
     "total_calendars": 5
   }
   ```

   b. Update your `.env` file with specific calendar IDs if needed:
   ```
   ALLOWED_CALENDAR_IDS=["primary", "family@group.calendar.google.com"]
   ```

   c. Initial calendar sync:
   ```sh
   curl -X POST -H "X-API-Key: your_secret_api_key_here" http://localhost:8000/calendar/sync-today
   ```

   Example response:
   ```json
   {
     "message": "Calendar sync completed",
     "sync_results": {
       "john.doe@gmail.com": {
         "total_events": 5,
         "events_by_calendar": {
           "john.doe@gmail.com": 3,
           "family@group.calendar.google.com": 2
         }
       },
       "jane.doe@gmail.com": {
         "total_events": 3,
         "events_by_calendar": {
           "jane.doe@gmail.com": 2,
           "work@group.calendar.google.com": 1
         }
       }
     },
     "total_events": 8,
     "accounts_processed": 2
   }
   ```

7. **Set Up Daily Sync:**
   Add to your crontab to sync daily at 11 PM:
   ```sh
   # Edit crontab
   crontab -e
   
   # Add this line (replace YOUR_API_KEY with your actual API key)
   0 23 * * * curl -X POST -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/calendar/sync-today
   ```

## Database Management

To update the database:

```sh
# Initialize Alembic (already done)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "description_of_changes"

# Apply migrations
alembic upgrade head
```

---

**Note:**  
- Make sure you have a `.env` file with your environment variables in the project root.
- The default API will be available on port `8000`.
- All API endpoints require authentication using the `X-API-Key` header.
- Google Calendar tokens are automatically saved in the `google_creds` directory as `{email_prefix}_token.pickle` files.
- The first time you run any calendar endpoint, it will require browser-based authentication.
- Token files are automatically refreshed when expired.
