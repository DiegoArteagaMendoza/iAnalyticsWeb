from apps.core.views import ManagementViewSet, SingletonManagementView
from apps.data_capabilities.models import DataCapability
from apps.data_capabilities.serializers import (
    DataCapabilitiesSectionManagementSerializer,
    DataCapabilityManagementSerializer,
)


class DataCapabilitiesSectionManagementView(SingletonManagementView):
    serializer_class = DataCapabilitiesSectionManagementSerializer


class DataCapabilityViewSet(ManagementViewSet):
    queryset = DataCapability.objects.all()
    serializer_class = DataCapabilityManagementSerializer
