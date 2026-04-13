import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrovalida.settings.production')

logger = logging.getLogger(__name__)

try:
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    call_command('migrate', '--noinput', verbosity=0)
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser('admin', 'admin@agrovalida.com', 'admin123')
except Exception as e:
    logger.error(f'Erro ao executar migrate/createadmin: {e}')

application = get_wsgi_application()