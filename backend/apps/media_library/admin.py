from django.contrib import admin
from django.utils.html import format_html

from apps.media_library.models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ["preview", "title", "file_name", "content_type", "size_kb", "uploaded_by", "created_at"]
    list_display_links = ["preview", "title"]
    search_fields = ["title", "file"]
    readonly_fields = ["preview", "content_type", "size_bytes", "uploaded_by", "created_at", "updated_at"]

    @admin.display(description="vista previa")
    def preview(self, obj):
        if obj.file and obj.is_image:
            return format_html('<img src="{}" style="max-height:48px;max-width:96px">', obj.file.url)
        return "—"

    @admin.display(description="tamaño (KB)")
    def size_kb(self, obj):
        return round(obj.size_bytes / 1024, 1)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
