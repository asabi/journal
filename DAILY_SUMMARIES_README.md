# Daily Summaries and Vector Search

This system creates AI-powered daily summaries from all your collected data and stores them in a Qdrant vector database for intelligent querying.

## Setup

1. Add the following to your `.env` file:
```
VECTOR_DB_URL=http://localhost:6333
OLLAMA_MODEL=gemma3:27b
OLLAMA_URL=http://100.119.144.30:11434
```

2. Make sure Qdrant is running on the specified URL
3. Ensure your Ollama model supports embeddings (or the system will use dummy embeddings)

## Endpoints

### 1. Create Daily Summary
**POST** `/summaries/create`

Creates a comprehensive daily summary for a specific date (defaults to yesterday).

**Parameters:**
- `target_date` (optional): Date in YYYY-MM-DD format

**Example:**
```bash
curl -X POST "http://localhost:8000/summaries/create?target_date=2024-06-01" \
  -H "X-API-Key: your-api-key"
```

**What it collects:**
- Calendar events (meetings, appointments)
- Food intake (calories, meal types)
- Health metrics (steps, heart rate, sleep)
- Exercise data
- Sleep analysis

### 2. Query Summaries
**GET** `/summaries/query`

Query your daily summaries using natural language.

**Parameters:**
- `q`: Natural language query
- `limit` (optional): Max number of summaries to consider (default: 5)

**Example queries:**
```bash
# What kind of days are most stressful?
curl -X GET "http://localhost:8000/summaries/query?q=What%20kind%20of%20days%20are%20most%20stressful%20for%20me?" \
  -H "X-API-Key: your-api-key"

# Days with most interviews
curl -X GET "http://localhost:8000/summaries/query?q=What%20days%20of%20the%20week%20do%20I%20have%20the%20most%20interviews?" \
  -H "X-API-Key: your-api-key"

# Sleep patterns
curl -X GET "http://localhost:8000/summaries/query?q=When%20do%20I%20sleep%20the%20best?" \
  -H "X-API-Key: your-api-key"

# Exercise impact
curl -X GET "http://localhost:8000/summaries/query?q=How%20does%20my%20exercise%20affect%20my%20sleep?" \
  -H "X-API-Key: your-api-key"
```

### 3. Get Recent Summaries
**GET** `/summaries/recent`

Get recent daily summaries without specific querying.

**Parameters:**
- `limit` (optional): Number of recent summaries (default: 7)

**Example:**
```bash
curl -X GET "http://localhost:8000/summaries/recent?limit=10" \
  -H "X-API-Key: your-api-key"
```

### 4. Bulk Create Summaries
**POST** `/summaries/bulk-create`

Create summaries for a range of dates (useful for backfilling).

**Parameters:**
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format

**Example:**
```bash
curl -X POST "http://localhost:8000/summaries/bulk-create?start_date=2024-05-01&end_date=2024-05-07" \
  -H "X-API-Key: your-api-key"
```

## How It Works

1. **Data Collection**: The system gathers all data for a specific date:
   - Calendar events from your Google Calendar
   - Food intake from analyzed images
   - Health metrics from Apple Health
   - Sleep data
   - Exercise information

2. **AI Summary Generation**: Uses your Ollama model to create a comprehensive summary that includes:
   - Overall day assessment
   - Key activities and meetings
   - Health and wellness highlights
   - Food intake patterns
   - Sleep quality assessment
   - Notable patterns or concerns

3. **Vector Storage**: The summary is converted to embeddings and stored in Qdrant with metadata for efficient semantic search.

4. **Intelligent Querying**: When you ask questions, the system:
   - Converts your query to embeddings
   - Finds relevant summaries using semantic search
   - Uses AI to analyze patterns and provide insights

## Example Use Cases

- **Productivity Analysis**: "What makes my most productive days?"
- **Health Patterns**: "How does my sleep affect my next day's energy?"
- **Stress Identification**: "What types of meetings stress me out the most?"
- **Nutrition Insights**: "How does my diet affect my workout performance?"
- **Weekly Patterns**: "What day of the week am I most active?"
- **Meeting Analysis**: "How many hours do I spend in meetings per week?"

## Data Privacy

All data is processed locally using your own Ollama instance and stored in your own Qdrant database. No data is sent to external AI services. 