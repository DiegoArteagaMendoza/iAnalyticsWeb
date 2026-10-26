import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image


def make_png(name="imagen.png", size=(8, 8)):
    buffer = io.BytesIO()
    Image.new("RGB", size, color=(242, 183, 5)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def make_staff_user(username="editor", superuser=True):
    user_model = get_user_model()
    if superuser:
        return user_model.objects.create_superuser(username=username, password="clave-segura-123")
    return user_model.objects.create_user(username=username, password="clave-segura-123", is_staff=True)


class TemporaryMediaMixin:
    """Guarda los archivos subidos en una carpeta temporal que se borra al terminar."""

    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp(prefix="ianalytics_test_media_")
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
