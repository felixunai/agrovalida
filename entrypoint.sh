#!/bin/bash
set -e
export DJANGO_SETTINGS_MODULE=agrovalida.settings.production

echo "=== Checking DATABASE_URL ==="
echo "DATABASE_URL is set: $(if [ -n \"$DATABASE_URL\" ]; then echo YES; else echo NO; fi)"
echo "DATABASE_PRIVATE_URL is set: $(if [ -n \"$DATABASE_PRIVATE_URL\" ]; then echo YES; else echo NO; fi)"

echo "=== Running migrations ==="
python manage.py migrate --noinput --settings=agrovalida.settings.production -v 2

echo "=== Creating admin user ==="
python manage.py createadmin --settings=agrovalida.settings.production

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --settings=agrovalida.settings.production

echo "=== Starting gunicorn ==="
exec gunicorn agrovalida.wsgi --log-file - --bind 0.0.0.0:${PORT:-8080}