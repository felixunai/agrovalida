import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrovalida.settings.production')

logger = logging.getLogger(__name__)

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

logger.info('=== Running migrations ===')
call_command('migrate', '--noinput', verbosity=2)
logger.info('=== Migrations complete ===')

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@agrovalida.com', 'admin123')
    logger.info('=== Superuser created ===')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()