from django.conf import settings
from django.db import models
from rest_framework import serializers


class LocalizedModelSerializer(serializers.ModelSerializer):
    """
    Serializador público: entrega cada campo traducible con su nombre lógico
    (`title` en vez de `title_es`/`title_en`) en el idioma de `context["language"]`.

    Meta.fields: campos no traducibles a incluir.
    Meta.translated_fields (opcional): traducibles a incluir; por defecto todos.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get("language", settings.CONTENT_SOURCE_LANGUAGE)
        names = getattr(self.Meta, "translated_fields", getattr(instance, "translatable_fields", []))
        for name in names:
            data[name] = instance.get_translation(name, language)
        return data


class ManagementModelSerializer(serializers.ModelSerializer):
    """
    Serializador de gestión: expone ambas versiones de cada texto (`_es` y `_en`).

    Las imágenes opcionales se pueden quitar enviando el campo vacío (multipart) o null (JSON);
    el archivo anterior se borra del disco (ver apps/core/signals.py).
    """

    class Meta:
        fields = "__all__"
        read_only_fields = ["auto_translations", "created_at", "updated_at"]

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(field_name, model_field)
        if isinstance(model_field, models.FileField) and model_field.blank:
            field_kwargs["allow_null"] = True
        return field_class, field_kwargs

    def validate(self, attrs):
        for name, value in attrs.items():
            if value is None and isinstance(self.Meta.model._meta.get_field(name), models.FileField):
                attrs[name] = ""
        return super().validate(attrs)


def management_serializer_for(model_class, **extra_meta):
    """Crea un serializador de gestión con todos los campos del modelo."""
    meta = type("Meta", (ManagementModelSerializer.Meta,), {"model": model_class, **extra_meta})
    return type(f"{model_class.__name__}ManagementSerializer", (ManagementModelSerializer,), {"Meta": meta})
