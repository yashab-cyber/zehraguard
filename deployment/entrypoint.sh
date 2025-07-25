#!/bin/bash
set -e

# ZehraGuard InsightX Docker Entrypoint Script

echo "Starting ZehraGuard InsightX..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is up - executing command"

# Wait for Redis
echo "Waiting for Redis..."
while ! redis-cli -h $REDIS_HOST -p 6379 -a $REDIS_PASSWORD ping > /dev/null 2>&1; do
    echo "Redis is unavailable - sleeping"
    sleep 1
done
echo "Redis is up"

# Wait for InfluxDB
echo "Waiting for InfluxDB..."
while ! curl -f $INFLUXDB_URL/ping > /dev/null 2>&1; do
    echo "InfluxDB is unavailable - sleeping"
    sleep 1
done
echo "InfluxDB is up"

# Run database migrations if needed
echo "Running database migrations..."
python -c "
import asyncio
import sys
sys.path.append('/app')
from core.database import Database

async def main():
    db = Database()
    await db.create_tables()
    print('Database tables created successfully')

asyncio.run(main())
"

# Initialize ML models
echo "Initializing ML models..."
python -c "
import asyncio
import sys
sys.path.append('/app')
from core.services.ml_service import MLService

async def main():
    ml_service = MLService()
    await ml_service.initialize()
    print('ML service initialized successfully')

asyncio.run(main())
"

echo "ZehraGuard InsightX initialization complete"

# Execute the main command
exec "$@"
