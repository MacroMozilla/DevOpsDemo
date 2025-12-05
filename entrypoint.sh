#!/bin/bash
set -e

echo "⏳ Waiting for the database (if applicable)..."
# If you're using PostgreSQL or MySQL, you can add a wait loop like this:
# until nc -z -v -w30 db 5432; do
#   echo "Waiting for database connection..."
#   sleep 3
# done

echo "📦 Applying database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn DevOpsDemo.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
