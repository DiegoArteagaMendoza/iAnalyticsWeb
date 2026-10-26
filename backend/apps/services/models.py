from django.db import models

from apps.core.models import ACCENT_COLOR_CHOICES, OrderedModel, SectionHeaderModel, TranslatableModel, TranslatedField


class ServicesSection(SectionHeaderModel):
    class Meta:
        verbose_name = "sección servicios"
        verbose_name_plural = "sección servicios"


class Service(OrderedModel, TranslatableModel):
    """Tarjeta de servicio (Aplicaciones a Medida, Asesorías, Visibilidad de Datos)."""

    tag = TranslatedField(models.CharField, "etiqueta", max_length=40, required=False)
    title = TranslatedField(models.CharField, "título", max_length=120)
    menu_description = TranslatedField(
        models.CharField, "descripción en el menú", max_length=160, required=False
    )
    description = TranslatedField(models.TextField, "descripción", required=False)
    link_text = TranslatedField(models.CharField, "texto del enlace", max_length=80, required=False)
    link_url = models.CharField("enlace", max_length=300, blank=True, default="")
    accent_color = models.CharField("color", max_length=10, choices=ACCENT_COLOR_CHOICES, default="yellow")

    class Meta(OrderedModel.Meta):
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return self.title_es


class ServiceFeature(TranslatableModel):
    service = models.ForeignKey(Service, verbose_name="servicio", on_delete=models.CASCADE, related_name="features")
    text = TranslatedField(models.CharField, "texto", max_length=200)
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        verbose_name = "característica"
        verbose_name_plural = "características"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text_es
