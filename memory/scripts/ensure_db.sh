#!/usr/bin/env bash

# Conditional debug logging (enable with CLAUDE_MEMORY_DEBUG=1)
DEBUG="${CLAUDE_MEMORY_DEBUG:-0}"
log_debug() {
  [ "$DEBUG" = "1" ] && echo "[ensure_db] $1" >&2
}

# Exit immediately if running in remote environment
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
  log_debug "Skipping: remote environment"
  exit 0
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
  log_debug "Skipping: docker not available"
  exit 0
fi

# Determine project directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Check if docker-compose.yml exists
if [ ! -f "$COMPOSE_FILE" ]; then
  log_debug "Skipping: docker-compose.yml not found at $COMPOSE_FILE"
  exit 0
fi

log_debug "Checking database status..."

# Quick check: if container is already running and healthy, exit immediately
if docker ps --format '{{.Names}}: {{.Status}}' 2>/dev/null | grep -q "pgvector.*healthy"; then
  log_debug "Container already healthy"
  exit 0
fi

# Check if pgvector container needs to be started
if ! docker compose -f "$COMPOSE_FILE" ps pgvector 2>/dev/null | grep -q "Up"; then
  log_debug "Starting pgvector container..."
  docker compose -f "$COMPOSE_FILE" up -d pgvector 2>/dev/null
fi

# Wait for database to be ready (up to 5 seconds with faster polling)
log_debug "Waiting for database (max 5s)..."
for i in {1..10}; do
  if docker compose -f "$COMPOSE_FILE" exec -T pgvector pg_isready -U ai -d ai &> /dev/null; then
    log_debug "Database ready"
    exit 0
  fi
  sleep 0.5
done

log_debug "Database not ready after timeout"
exit 0
