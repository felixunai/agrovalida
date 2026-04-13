#!/bin/bash
set -e
echo "Running migrations..."
python manage.py migrate --noinput
echo "Creating admin user..."
python manage.py createadmin
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Starting gunicorn..."
exec gunicorn agrovalida.wsgi --log-file - --bind 0.0.0.0:${PORT:-8080}