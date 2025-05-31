#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting deployment process..."

# Pull latest changes
echo "📥 Pulling latest changes from git..."
git pull

# Build new Docker image
echo "🏗️  Building Docker image..."
docker build -t life-journal-api .

# Stop and remove existing container
echo "🛑 Stopping existing container..."
docker stop journal || true
docker rm journal || true

# Run new container
echo "🚀 Starting new container..."
docker run -d -p 8000:8000 --env-file .env --restart unless-stopped --name journal life-journal-api

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 5

# Run database migrations (only if there are new ones)
echo "🔄 Checking and running database migrations..."
docker exec journal bash -c '
current_rev=$(alembic current | cut -d" " -f1)
head_rev=$(alembic heads | cut -d" " -f1)
if [ "$current_rev" != "$head_rev" ]; then
    echo "New migrations found, upgrading database..."
    alembic upgrade head
else
    echo "Database is up to date, no migrations needed."
fi
'

echo "✅ Deployment completed successfully!"
echo "📝 You can check the logs with: docker logs journal"
echo "🌐 API is available at: http://localhost:8000/docs"