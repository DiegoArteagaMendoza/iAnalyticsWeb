from apps.core.views import ManagementViewSet, SingletonManagementView
from apps.services.models import Service, ServiceFeature
from apps.services.serializers import (
    ServiceFeatureManagementSerializer,
    ServiceManagementSerializer,
    ServicesSectionManagementSerializer,
)


class ServicesSectionManagementView(SingletonManagementView):
    serializer_class = ServicesSectionManagementSerializer


class ServiceViewSet(ManagementViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceManagementSerializer


class ServiceFeatureViewSet(ManagementViewSet):
    """Características de cada servicio. Filtrar con ?service=<id>."""

    queryset = ServiceFeature.objects.select_related("service")
    serializer_class = ServiceFeatureManagementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get("service")
        if service_id and service_id.isdigit():
            queryset = queryset.filter(service_id=service_id)
        return queryset
