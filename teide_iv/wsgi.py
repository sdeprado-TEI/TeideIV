import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teide_iv.settings')

# Configuración inicial
django.setup()

try:
    # 1. Ejecutar migraciones solo una vez
    call_command('migrate', '--noinput')

    # 2. Crear usuarios solo si no existen
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@teide.es', 'adminteideIV')
        print("Usuario admin creado")

    if not User.objects.filter(username='profesor').exists():
        profesor = User.objects.create_user('profesor', 'profesor@teide.es', 'profesorteideIV')
        profesor.is_staff = True
        profesor.save()
        print("Usuario profesor creado")

except Exception as e:
    # Si falla, imprimimos el error en los logs para saber qué pasa
    print(f"Error crítico en wsgi: {e}")

application = get_wsgi_application()
app = application
