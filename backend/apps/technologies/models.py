from django.db import models

from apps.core.models import OrderedModel, SectionHeaderModel, TimeStampedModel, TranslatedField
from apps.core.validators import IMAGE_VALIDATORS


class TechnologiesSection(SectionHeaderModel):
    development_label = TranslatedField(models.CharField, "leyenda desarrollo", max_length=80, required=False)
    data_label = TranslatedField(models.CharField, "leyenda datos", max_length=80, required=False)

    class Meta:
        verbose_name = "sección tecnologías"
        verbose_name_plural = "sección tecnologías"


class Technology(OrderedModel, TimeStampedModel):
    class Category(models.TextChoices):
        DEVELOPMENT = "development", "Desarrollo web y mobile"
        DATA = "data", "Datos e inteligencia de negocios"

    name = models.CharField("nombre", max_length=80)
    category = models.CharField("categoría", max_length=20, choices=Category.choices, default=Category.DEVELOPMENT)
    logo = models.FileField("logo (opcional)", upload_to="technologies/", validators=IMAGE_VALIDATORS, blank=True)
    website_url = models.URLField("sitio web", blank=True, default="")

    class Meta(OrderedModel.Meta):
        verbose_name = "tecnología"
        verbose_name_plural = "tecnologías"
        ordering = ["category", "order", "id"]

    def __str__(self):
        return self.name
