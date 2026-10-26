from django.db import models

from apps.core.models import ACCENT_COLOR_CHOICES, OrderedModel, SingletonModel, TranslatableModel, TranslatedField
from apps.core.validators import IMAGE_VALIDATORS


class HeroSection(SingletonModel, TranslatableModel):
    """Portada: titular en dos líneas, párrafo y dos botones."""

    eyebrow = TranslatedField(models.CharField, "etiqueta superior", max_length=80, required=False)
    title_line_1 = TranslatedField(models.CharField, "título (línea 1)", max_length=160, required=False)
    title_line_2 = TranslatedField(
        models.CharField, "título (línea 2, destacada)", max_length=160, required=False
    )
    lead = TranslatedField(models.TextField, "párrafo", required=False)
    primary_cta_text = TranslatedField(models.CharField, "botón principal: texto", max_length=80, required=False)
    primary_cta_url = models.CharField("botón principal: enlace", max_length=300, blank=True, default="#contacto")
    secondary_cta_text = TranslatedField(
        models.CharField, "botón secundario: texto", max_length=80, required=False
    )
    secondary_cta_url = models.CharField("botón secundario: enlace", max_length=300, blank=True, default="#servicios")
    background_image = models.FileField(
        "imagen de fondo (opcional)",
        upload_to="hero/",
        validators=IMAGE_VALIDATORS,
        blank=True,
        help_text="Si se deja vacía se usa la animación de red de datos.",
    )

    class Meta:
        verbose_name = "portada"
        verbose_name_plural = "portada"

    def __str__(self):
        return "Portada"


class HeroHighlight(OrderedModel, TranslatableModel):
    """Etiquetas bajo los botones de la portada."""

    text = TranslatedField(models.CharField, "texto", max_length=80)
    accent_color = models.CharField("color", max_length=10, choices=ACCENT_COLOR_CHOICES, default="yellow")

    class Meta(OrderedModel.Meta):
        verbose_name = "etiqueta destacada"
        verbose_name_plural = "etiquetas destacadas"

    def __str__(self):
        return self.text_es
