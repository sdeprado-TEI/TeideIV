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
# ... (lo que ya tienes de migrate) ...
try:
    django.setup()
    call_command('migrate', '--noinput')

    # Crear Administrador
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@teide.es', 'adminteideIV')
        print("Usuario admin creado")

    # Crear Profesor
    if not User.objects.filter(username='profesor').exists():
        profesor = User.objects.create_user('profesor', 'profesor@teide.es', 'profesorteideIV')
        profesor.is_staff = True  # O si prefieres que tenga acceso limitado, puedes quitar esta línea
        profesor.save()
        print("Usuario profesor creado")

except Exception as e:
    print(f"Error: {e}")
