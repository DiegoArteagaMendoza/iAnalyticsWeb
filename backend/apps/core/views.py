from django.db import connection
from django.db.utils import OperationalError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

FILE_PARSERS = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]


class HealthView(APIView):
    """Estado del servicio y de la conexión a la base de datos (usado por Docker)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        try:
            connection.ensure_connection()
        except OperationalError:
            return Response({"status": "error", "database": "unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"status": "ok", "database": "ok"})


class SingletonManagementView(generics.RetrieveUpdateAPIView):
    """GET / PUT / PATCH del único registro de una sección (sus textos e imágenes)."""

    parser_classes = FILE_PARSERS

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def get_object(self):
        instance = self.serializer_class.Meta.model.load()
        self.check_object_permissions(self.request, instance)
        return instance


class ManagementViewSet(viewsets.ModelViewSet):
    """CRUD de los elementos de una sección (tarjetas, personas, logos, etc.)."""

    parser_classes = FILE_PARSERS
