from django.http import FileResponse, Http404
from rest_framework import filters
from rest_framework.decorators import action

from apps.core.views import ManagementViewSet
from apps.media_library.models import MediaFile
from apps.media_library.serializers import MediaFileSerializer


class MediaFileViewSet(ManagementViewSet):
    """
    Biblioteca de archivos.
    - Subir: POST multipart con `title` y `file`.
    - Reemplazar: PATCH multipart con un nuevo `file` (el anterior se borra del disco).
    - Descargar: GET /media_files/<id>/download/
    - Eliminar: DELETE (borra también el archivo del disco).
    Buscar con ?search=<texto>.
    """

    queryset = MediaFile.objects.select_related("uploaded_by")
    serializer_class = MediaFileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "file", "alt_text_es", "alt_text_en"]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        media_file = self.get_object()
        if not media_file.file or not media_file.file.storage.exists(media_file.file.name):
            raise Http404("El archivo no existe en el servidor.")
        return FileResponse(
            media_file.file.open("rb"),
            as_attachment=True,
            filename=media_file.file_name,
            content_type=media_file.content_type or None,
        )
