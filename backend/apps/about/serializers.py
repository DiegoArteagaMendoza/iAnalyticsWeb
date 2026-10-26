from apps.about.models import AboutSection, CompanyValue
from apps.core.serializers import LocalizedModelSerializer, management_serializer_for

AboutSectionManagementSerializer = management_serializer_for(AboutSection)
CompanyValueManagementSerializer = management_serializer_for(CompanyValue)


class CompanyValuePublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = CompanyValue
        fields = ["id", "order", "is_published", "accent_color"]


class AboutSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = AboutSection
        fields = ["cta_url"]
