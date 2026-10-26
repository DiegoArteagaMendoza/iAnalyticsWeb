from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.services.models import Service, ServiceFeature, ServicesSection

ServicesSectionManagementSerializer = management_serializer_for(ServicesSection)
ServiceManagementSerializer = management_serializer_for(Service)
ServiceFeatureManagementSerializer = management_serializer_for(ServiceFeature)


class ServiceFeaturePublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = ServiceFeature
        fields = ["id", "order"]


class ServicePublicSerializer(LocalizedModelSerializer):
    features = ServiceFeaturePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ["id", "order", "is_published", "link_url", "accent_color", "features"]


class ServicesSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = ServicesSection
        fields = ["cta_url"]
