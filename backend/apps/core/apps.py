from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Núcleo"

    def ready(self):
        from apps.core import signals

        signals.connect_file_cleanup()
