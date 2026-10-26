import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Espera hasta que la base de datos acepte conexiones."

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=60, help="Segundos máximos de espera.")

    def handle(self, *args, timeout, **options):
        deadline = time.monotonic() + timeout
        while True:
            try:
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Base de datos disponible."))
                return
            except OperationalError as error:
                if time.monotonic() >= deadline:
                    raise CommandError(f"La base de datos no respondió en {timeout} s: {error}") from error
                self.stdout.write("Esperando la base de datos...")
                connection.close()
                time.sleep(2)
