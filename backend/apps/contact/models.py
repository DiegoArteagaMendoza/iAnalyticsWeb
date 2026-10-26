from django.db import models

from apps.core.models import SectionHeaderModel, TimeStampedModel, TranslatedField


class ContactSection(SectionHeaderModel):
    """Textos de la sección de contacto, del banner de cierre y del formulario."""

    banner_title = TranslatedField(models.CharField, "banner de cierre: título", max_length=160, required=False)
    banner_button_text = TranslatedField(
        models.CharField, "banner de cierre: botón", max_length=80, required=False
    )
    form_submit_text = TranslatedField(models.CharField, "formulario: botón enviar", max_length=80, required=False)
    form_success_message = TranslatedField(
        models.CharField, "formulario: mensaje de éxito", max_length=200, required=False
    )
    form_other_option = TranslatedField(
        models.CharField, "formulario: opción 'Otro'", max_length=60, required=False
    )

    class Meta:
        verbose_name = "sección contacto"
        verbose_name_plural = "sección contacto"


class ContactMessage(TimeStampedModel):
    """Mensaje enviado desde el formulario de la página."""

    full_name = models.CharField("nombre", max_length=120)
    company = models.CharField("empresa", max_length=120, blank=True, default="")
    email = models.EmailField("e-mail")
    phone = models.CharField("teléfono", max_length=40, blank=True, default="")
    service_of_interest = models.CharField("servicio de interés", max_length=120, blank=True, default="")
    message = models.TextField("mensaje", max_length=5000, blank=True, default="")
    language = models.CharField("idioma de la página", max_length=5, default="es")
    is_read = models.BooleanField("leído", default=False)

    class Meta:
        verbose_name = "mensaje de contacto"
        verbose_name_plural = "mensajes de contacto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
