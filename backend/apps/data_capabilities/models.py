from django.db import models

from apps.core.models import OrderedModel, SectionHeaderModel, TranslatableModel, TranslatedField


class DataCapabilitiesSection(SectionHeaderModel):
    class Meta:
        verbose_name = "sección visibilidad de datos"
        verbose_name_plural = "sección visibilidad de datos"


class DataCapability(OrderedModel, TranslatableModel):
    """Tarjeta del carrusel de datos (Datawarehouse, Datamart, Informes, etc.)."""

    title = TranslatedField(models.CharField, "título", max_length=120)
    description = TranslatedField(models.TextField, "descripción", required=False)

    class Meta(OrderedModel.Meta):
        verbose_name = "capacidad de datos"
        verbose_name_plural = "capacidades de datos"

    def __str__(self):
        return self.title_es
