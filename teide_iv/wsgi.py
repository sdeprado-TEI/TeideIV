import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teide_iv.settings')

# Intentamos ejecutar las migraciones automáticamente al arrancar
try:
    django.setup()
    call_command('migrate', '--noinput')
except Exception as e:
    print(f"Error en migración automática: {e}")

application = get_wsgi_application()

app = application
