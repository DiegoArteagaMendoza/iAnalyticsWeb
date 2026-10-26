import mimetypes
from pathlib import Path

from django.conf import settings
from django.db import models

from apps.core.models import TranslatableModel, TranslatedField
from apps.core.validators import IMAGE_EXTENSIONS, MEDIA_VALIDATORS


class MediaFile(TranslatableModel):
    """Archivo subido a la biblioteca (imágenes, documentos) para usar en la página."""

    title = models.CharField("título", max_length=160)
    file = models.FileField("archivo", upload_to="media_library/%Y/%m/", validators=MEDIA_VALIDATORS)
    alt_text = TranslatedField(
        models.CharField, "texto alternativo", max_length=200, required=False,
        help_text="Describe la imagen para lectores de pantalla y buscadores.",
    )
    content_type = models.CharField("tipo de archivo", max_length=100, blank=True, default="", editable=False)
    size_bytes = models.PositiveBigIntegerField("tamaño (bytes)", default=0, editable=False)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="subido por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        verbose_name = "archivo"
        verbose_name_plural = "biblioteca de archivos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def file_name(self):
        return Path(self.file.name).name if self.file else ""

    @property
    def is_image(self):
        return Path(self.file_name).suffix.lower().lstrip(".") in IMAGE_EXTENSIONS

    def save(self, *args, **kwargs):
        if self.file:
            self.size_bytes = self.file.size
            self.content_type = mimetypes.guess_type(self.file.name)[0] or "application/octet-stream"
        super().save(*args, **kwargs)
