import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Crea el administrador inicial desde DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD "
        "y DJANGO_SUPERUSER_EMAIL si todavía no existe. Nunca cambia la clave de un usuario existente."
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD no definidos: no se crea administrador.")
            return

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"El administrador '{username}' ya existe.")
            return
        user_model.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Administrador '{username}' creado."))
