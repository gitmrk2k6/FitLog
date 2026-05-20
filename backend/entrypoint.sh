#!/bin/bash
set -e

# DB_PASSWORD は ECS タスク定義の secrets[] ブロック経由で Secrets Manager から注入される。
# Pydantic Settings は DATABASE_URL を単一文字列として読むため、ここで組み立てて export する。
export DATABASE_URL="postgresql+psycopg://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:5432/fitlog"

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --log-level info
