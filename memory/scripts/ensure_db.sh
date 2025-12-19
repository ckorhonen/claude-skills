#!/usr/bin/env bash

# Exit immediately if running in remote environment
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
  exit 0
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
  echo "Docker not available, skipping database setup"
  exit 0
fi

# Determine project directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Check if pgvector container is running
if ! docker compose -f "$PROJECT_DIR/docker-compose.yml" ps pgvector 2>/dev/null | grep -q "Up"; then
  echo "Starting pgvector container..."
  docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d pgvector
fi

# Wait for database to be ready (up to 10 seconds)
echo "Waiting for database to be ready..."
for i in {1..10}; do
  if docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T pgvector pg_isready -U ai -d ai &> /dev/null; then
    echo "Database is ready"
    exit 0
  fi
  sleep 1
done

echo "Database not ready after 10 seconds, continuing anyway"
exit 0
