from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.data_capabilities.models import DataCapabilitiesSection, DataCapability

DataCapabilitiesSectionManagementSerializer = management_serializer_for(DataCapabilitiesSection)
DataCapabilityManagementSerializer = management_serializer_for(DataCapability)


class DataCapabilityPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = DataCapability
        fields = ["id", "order", "is_published"]


class DataCapabilitiesSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = DataCapabilitiesSection
        fields = ["cta_url"]
