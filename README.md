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

---

**Note:**  
- Make sure you have a `.env` file with your environment variables in the project root.
- The default API will be available on port `8000`.

To update the database:

alembic init alembic (done already)

Example:

alembic revision --autogenerate -m "add units to health_data"
alembic upgrade head
