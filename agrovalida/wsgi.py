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
    admin = User.objects.create_superuser('admin', 'admin@agrovalida.com', 'admin123')
    logger.info('=== Superuser created ===')
    from accounts.models import Plano, UserProfile
    plano_pro, _ = Plano.objects.get_or_create(nome='Profissional', defaults={'preco': 500, 'descricao': 'Acesso completo ao sistema com todas as funcionalidades', 'ativo': True})
    profile, _ = UserProfile.objects.get_or_create(user=admin, defaults={'plano': plano_pro, 'plano_ativo': True})

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info('=== WSGI application loaded successfully ===')
except Exception as _wsgi_err:
    import traceback, sys
    print('=== WSGI STARTUP ERROR ===', flush=True)
    traceback.print_exc(file=sys.stdout)
    sys.stdout.flush()
    raise