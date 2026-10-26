from django.db import models

from apps.core.models import ACCENT_COLOR_CHOICES, OrderedModel, SectionHeaderModel, TranslatableModel, TranslatedField
from apps.core.validators import IMAGE_VALIDATORS


class TeamSection(SectionHeaderModel):
    founders_label = TranslatedField(models.CharField, "subtítulo fundadores", max_length=80, required=False)
    members_label = TranslatedField(models.CharField, "subtítulo equipo", max_length=80, required=False)

    class Meta:
        verbose_name = "sección equipo"
        verbose_name_plural = "sección equipo"


class TeamMember(OrderedModel, TranslatableModel):
    full_name = models.CharField("nombre completo", max_length=120)
    role = TranslatedField(models.CharField, "cargo", max_length=120)
    bio = TranslatedField(models.TextField, "reseña", required=False)
    photo = models.FileField("foto", upload_to="team/", validators=IMAGE_VALIDATORS, blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True, default="")
    is_founder = models.BooleanField("es fundador/a", default=False)
    accent_color = models.CharField("color de acento", max_length=10, choices=ACCENT_COLOR_CHOICES, default="yellow")

    class Meta:
        verbose_name = "integrante del equipo"
        verbose_name_plural = "integrantes del equipo"
        ordering = ["-is_founder", "order", "id"]

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        return "".join(part[0] for part in self.full_name.split()[:2]).upper()
