"""Modelos base compartidos por todas las secciones de la página."""
from django.conf import settings
from django.db import models

from apps.core.translation import services as translation_services

ACCENT_COLOR_CHOICES = [
    ("yellow", "Amarillo"),
    ("green", "Verde"),
    ("blue", "Azul"),
    ("base", "Base (azul tinta)"),
]


class TranslatedField:
    """
    Declara un campo traducible. Crea dos columnas reales: `<nombre>_es` y `<nombre>_en`.

        title = TranslatedField(models.CharField, "título", max_length=200)

    El español es el idioma fuente (obligatorio salvo required=False); el inglés
    siempre es opcional porque se completa con la traducción automática.
    """

    def __init__(self, field_class, verbose_name, *, required=True, **field_kwargs):
        self.field_class = field_class
        self.verbose_name = verbose_name
        self.required = required
        self.field_kwargs = field_kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        source_language = settings.CONTENT_SOURCE_LANGUAGE
        language_labels = {"es": "español", "en": "inglés"}
        for language in settings.CONTENT_LANGUAGES:
            is_source = language == source_language
            field = self.field_class(
                verbose_name=f"{self.verbose_name} ({language_labels.get(language, language)})",
                blank=not (is_source and self.required),
                default="",
                **self.field_kwargs,
            )
            cls.add_to_class(f"{name}_{language}", field)

        if "translatable_fields" not in cls.__dict__:
            cls.translatable_fields = list(getattr(cls, "translatable_fields", []))
        cls.translatable_fields.append(name)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    order = models.PositiveIntegerField("orden", default=0, db_index=True)
    is_published = models.BooleanField("publicado", default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class TranslatableModel(TimeStampedModel):
    """
    Traduce automáticamente los campos traducibles al guardar.

    Reglas por campo:
    - Si el texto en inglés está vacío, se traduce.
    - Si el inglés fue generado automáticamente y el español cambió, se vuelve a traducir.
    - Si el inglés fue escrito a mano (distinto de la última traducción automática),
      se respeta y no se sobrescribe.
    """

    translatable_fields: list = []

    auto_translations = models.JSONField(
        "traducciones automáticas",
        default=dict,
        blank=True,
        editable=False,
        help_text="Registro interno del último texto traducido automáticamente por campo.",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.apply_auto_translations()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | self._translation_columns()
        super().save(*args, **kwargs)

    def _translation_columns(self):
        columns = {"auto_translations"}
        for name in self.translatable_fields:
            columns.update(f"{name}_{language}" for language in settings.CONTENT_LANGUAGES)
        return columns

    def apply_auto_translations(self, force=False):
        source_language = settings.CONTENT_SOURCE_LANGUAGE
        for target_language in settings.CONTENT_LANGUAGES:
            if target_language == source_language:
                continue
            for name in self.translatable_fields:
                self._translate_field(name, source_language, target_language, force)

    def _translate_field(self, name, source_language, target_language, force):
        source_text = getattr(self, f"{name}_{source_language}") or ""
        target_attr = f"{name}_{target_language}"
        current_text = getattr(self, target_attr) or ""
        record_key = f"{name}_{target_language}"
        previous = self.auto_translations.get(record_key)

        if not source_text.strip():
            return
        was_auto = previous is not None and current_text == previous.get("result")
        source_changed = previous is None or previous.get("source") != source_text
        needs_translation = force or not current_text.strip() or (was_auto and source_changed)
        if not needs_translation:
            return

        translated = translation_services.translate_text(source_text, source_language, target_language)
        if translated is None:
            return
        setattr(self, target_attr, translated)
        self.auto_translations[record_key] = {"source": source_text, "result": translated}

    def mark_as_auto_translated(self):
        """Marca las traducciones actuales como automáticas (usado al cargar contenido inicial)."""
        source_language = settings.CONTENT_SOURCE_LANGUAGE
        for target_language in settings.CONTENT_LANGUAGES:
            if target_language == source_language:
                continue
            for name in self.translatable_fields:
                source_text = getattr(self, f"{name}_{source_language}")
                target_text = getattr(self, f"{name}_{target_language}")
                if source_text and target_text:
                    self.auto_translations[f"{name}_{target_language}"] = {
                        "source": source_text,
                        "result": target_text,
                    }

    def get_translation(self, name, language):
        """Devuelve el texto en el idioma pedido, con respaldo al idioma fuente."""
        value = getattr(self, f"{name}_{language}", "") or ""
        if value.strip():
            return value
        return getattr(self, f"{name}_{settings.CONTENT_SOURCE_LANGUAGE}", "") or ""


class SingletonModel(models.Model):
    """Modelo con un único registro (pk=1), para los textos de cada sección."""

    singleton_pk = 1

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = self.singleton_pk
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Las secciones no se pueden eliminar, solo editar.")

    @classmethod
    def load(cls):
        instance = cls.objects.filter(pk=cls.singleton_pk).first()
        if instance is None:
            instance = cls(pk=cls.singleton_pk)
            instance.save()
        return instance


class SectionHeaderModel(SingletonModel, TranslatableModel):
    """Encabezado estándar de sección: etiqueta, título en dos líneas, párrafo y CTA."""

    is_visible = models.BooleanField("sección visible", default=True)
    eyebrow = TranslatedField(models.CharField, "etiqueta superior", max_length=80, required=False)
    title_line_1 = TranslatedField(models.CharField, "título (línea 1)", max_length=160, required=False)
    title_line_2 = TranslatedField(models.CharField, "título (línea 2)", max_length=160, required=False)
    body = TranslatedField(models.TextField, "párrafo", required=False)
    cta_text = TranslatedField(models.CharField, "texto del botón", max_length=80, required=False)
    cta_url = models.CharField("enlace del botón", max_length=300, blank=True, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self._meta.verbose_name)
