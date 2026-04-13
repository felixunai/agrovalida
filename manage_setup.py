#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrovalida.settings.production')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

print('=== Running migrations ===')
call_command('migrate', '--noinput', verbosity=1)
print('=== Migrations complete ===')

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@agrovalida.com', 'admin123')
    print('=== Superuser created ===')

print('=== Setup complete ===')