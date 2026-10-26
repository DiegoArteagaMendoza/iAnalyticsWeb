from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.technologies.models import TechnologiesSection, Technology

TechnologiesSectionManagementSerializer = management_serializer_for(TechnologiesSection)
TechnologyManagementSerializer = management_serializer_for(Technology)


class TechnologyPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = Technology
        fields = ["id", "order", "is_published", "name", "category", "logo", "website_url"]


class TechnologiesSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = TechnologiesSection
        fields = ["cta_url"]
