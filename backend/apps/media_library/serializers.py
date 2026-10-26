from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.media_library.models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True)
    is_image = serializers.BooleanField(read_only=True)
    download_url = serializers.SerializerMethodField()
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = MediaFile
        fields = [
            "id",
            "title",
            "file",
            "file_name",
            "is_image",
            "content_type",
            "size_bytes",
            "alt_text_es",
            "alt_text_en",
            "download_url",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["content_type", "size_bytes", "created_at", "updated_at"]

    @extend_schema_field(OpenApiTypes.URI)
    def get_download_url(self, instance):
        return reverse("media_file-download", args=[instance.pk], request=self.context.get("request"))
