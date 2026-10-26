from django.db import models

from apps.core.models import (
    ACCENT_COLOR_CHOICES,
    OrderedModel,
    SectionHeaderModel,
    TimeStampedModel,
    TranslatableModel,
    TranslatedField,
)
from apps.core.validators import IMAGE_VALIDATORS


class ClientsSection(SectionHeaderModel):
    class Meta:
        verbose_name = "sección clientes"
        verbose_name_plural = "sección clientes"


class Client(OrderedModel, TimeStampedModel):
    name = models.CharField("nombre", max_length=120)
    logo = models.FileField("logo", upload_to="clients/", validators=IMAGE_VALIDATORS, blank=True)
    website_url = models.URLField("sitio web", blank=True, default="")
    accent_color = models.CharField(
        "color (si no hay logo)", max_length=10, choices=ACCENT_COLOR_CHOICES, default="yellow"
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "cliente destacado"
        verbose_name_plural = "clientes destacados"

    def __str__(self):
        return self.name


class Testimonial(OrderedModel, TranslatableModel):
    quote = TranslatedField(models.TextField, "testimonio")
    author_name = models.CharField("nombre", max_length=120)
    author_role = TranslatedField(models.CharField, "cargo", max_length=120, required=False)
    company_name = models.CharField("empresa", max_length=120, blank=True, default="")
    photo = models.FileField("foto (opcional)", upload_to="testimonials/", validators=IMAGE_VALIDATORS, blank=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "testimonio"
        verbose_name_plural = "testimonios"

    def __str__(self):
        return f"{self.author_name} · {self.company_name}".strip(" ·")


class Certification(OrderedModel, TranslatableModel):
    badge_text = TranslatedField(models.CharField, "texto destacado", max_length=20, required=False)
    title = TranslatedField(models.CharField, "título", max_length=120)
    issuer = TranslatedField(models.CharField, "otorgada por", max_length=160, required=False)
    image = models.FileField("imagen (opcional)", upload_to="certifications/", validators=IMAGE_VALIDATORS, blank=True)
    accent_color = models.CharField("color", max_length=10, choices=ACCENT_COLOR_CHOICES, default="green")

    class Meta(OrderedModel.Meta):
        verbose_name = "certificación"
        verbose_name_plural = "certificaciones"

    def __str__(self):
        return self.title_es
