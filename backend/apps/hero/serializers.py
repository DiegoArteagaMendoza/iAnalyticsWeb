from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.hero.models import HeroHighlight, HeroSection

HeroSectionManagementSerializer = management_serializer_for(HeroSection)
HeroHighlightManagementSerializer = management_serializer_for(HeroHighlight)


class HeroHighlightPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = HeroHighlight
        fields = ["id", "order", "is_published", "accent_color"]


class HeroSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = HeroSection
        fields = ["primary_cta_url", "secondary_cta_url", "background_image"]
