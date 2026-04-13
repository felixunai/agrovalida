import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrovalida.settings.production')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

print('=== Running migrations ===')
call_command('migrate', '--noinput', verbosity=2)

print('=== Creating admin user ===')
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@agrovalida.com', 'admin123')
    print('Superuser "admin" created with password "admin123"')
else:
    print('Superuser already exists, skipping.')

print('=== Collecting static files ===')
call_command('collectstatic', '--noinput')

print('=== Setup complete ===')