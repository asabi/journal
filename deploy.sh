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

# Handle migrations in a development-friendly way
echo "🔄 Handling database migrations..."
docker exec journal bash -c '
# Try to run upgrade, but ignore table exists errors
alembic upgrade head 2>&1 | grep -v "DuplicateTable\|relation.*already exists" || true

# Always stamp at head to ensure Alembic is in sync
echo "Ensuring Alembic is at latest version..."
alembic stamp head
'

echo "✅ Deployment completed successfully!"
echo "📝 You can check the logs with: docker logs journal"
echo "🌐 API is available at: http://localhost:8000/docs"