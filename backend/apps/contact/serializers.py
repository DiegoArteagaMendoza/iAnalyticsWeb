from django.conf import settings
from rest_framework import serializers

from apps.contact.models import ContactMessage, ContactSection
from apps.core.serializers import LocalizedModelSerializer, management_serializer_for

ContactSectionManagementSerializer = management_serializer_for(ContactSection)


class ContactSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = ContactSection
        fields = ["cta_url"]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Formulario público. `website` es un campo trampa: los humanos lo dejan vacío."""

    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactMessage
        fields = ["full_name", "company", "email", "phone", "service_of_interest", "message", "language", "website"]
        extra_kwargs = {"language": {"required": False}}

    def validate_language(self, value):
        return value if value in settings.CONTENT_LANGUAGES else settings.CONTENT_SOURCE_LANGUAGE

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Solicitud rechazada.")
        return value

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)


class ContactMessageManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = [
            "full_name",
            "company",
            "email",
            "phone",
            "service_of_interest",
            "message",
            "language",
            "created_at",
            "updated_at",
        ]
