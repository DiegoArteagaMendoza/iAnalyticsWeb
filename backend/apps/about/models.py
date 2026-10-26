from django.db import models

from apps.core.models import ACCENT_COLOR_CHOICES, OrderedModel, SectionHeaderModel, TranslatableModel, TranslatedField


class AboutSection(SectionHeaderModel):
    """Quiénes somos: presentación, misión y visión."""

    mission = TranslatedField(models.TextField, "misión", required=False)
    vision = TranslatedField(models.TextField, "visión", required=False)

    class Meta:
        verbose_name = "sección nosotros"
        verbose_name_plural = "sección nosotros"


class CompanyValue(OrderedModel, TranslatableModel):
    name = TranslatedField(models.CharField, "valor", max_length=80)
    description = TranslatedField(models.CharField, "descripción", max_length=200, required=False)
    accent_color = models.CharField("color", max_length=10, choices=ACCENT_COLOR_CHOICES, default="yellow")

    class Meta(OrderedModel.Meta):
        verbose_name = "valor"
        verbose_name_plural = "valores"

    def __str__(self):
        return self.name_es
