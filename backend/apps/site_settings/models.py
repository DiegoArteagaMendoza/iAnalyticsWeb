from django.db import models

from apps.core.models import SingletonModel, TranslatableModel, TranslatedField
from apps.core.validators import IMAGE_VALIDATORS


def image_field(verbose_name):
    return models.FileField(verbose_name, upload_to="site_settings/", validators=IMAGE_VALIDATORS, blank=True)


class SiteSettings(SingletonModel, TranslatableModel):
    """Identidad, datos de contacto y SEO: lo que aparece en encabezado y footer."""

    company_name = models.CharField("nombre de la empresa", max_length=120, default="Informatic Analytics")

    logo_mark = image_field("logo: símbolo")
    logo_wordmark = image_field("logo: texto (fondo claro)")
    logo_wordmark_light = image_field("logo: texto (fondo oscuro)")
    logo_full = image_field("logo completo")
    favicon = image_field("favicon")

    meta_title = TranslatedField(models.CharField, "título de la pestaña (SEO)", max_length=120, required=False)
    meta_description = TranslatedField(models.CharField, "descripción (SEO)", max_length=300, required=False)

    phone_display = models.CharField("teléfono (como se muestra)", max_length=40, blank=True, default="")
    phone_link = models.CharField(
        "teléfono (para marcar)", max_length=40, blank=True, default="", help_text="Formato internacional, ej: +56422252035"
    )
    email = models.EmailField("e-mail", blank=True, default="")
    address = models.CharField("dirección", max_length=200, blank=True, default="")
    maps_url = models.URLField("enlace a Google Maps", blank=True, default="")
    business_hours = TranslatedField(models.CharField, "horario de atención", max_length=120, required=False)
    footer_tagline = TranslatedField(models.CharField, "frase del footer", max_length=200, required=False)
    translation_notice = TranslatedField(
        models.CharField, "aviso de traducción automática", max_length=200, required=False
    )

    linkedin_url = models.URLField("LinkedIn", blank=True, default="")
    facebook_url = models.URLField("Facebook", blank=True, default="")
    instagram_url = models.URLField("Instagram", blank=True, default="")
    youtube_url = models.URLField("YouTube", blank=True, default="")

    class Meta:
        verbose_name = "configuración del sitio"
        verbose_name_plural = "configuración del sitio"

    def __str__(self):
        return "Configuración del sitio"
