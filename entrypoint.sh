#!/bin/sh
set -e

echo "Starting Professional Hubs API..."
echo "Running database migrations..."

# Run Alembic migrations
alembic upgrade head

echo "Migrations complete. Starting server..."

# Start Gunicorn with Uvicorn workers
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --log-level info