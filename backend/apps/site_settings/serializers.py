from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.site_settings.models import SiteSettings

SiteSettingsManagementSerializer = management_serializer_for(SiteSettings)


class SiteSettingsPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "company_name",
            "logo_mark",
            "logo_wordmark",
            "logo_wordmark_light",
            "logo_full",
            "favicon",
            "phone_display",
            "phone_link",
            "email",
            "address",
            "maps_url",
            "linkedin_url",
            "facebook_url",
            "instagram_url",
            "youtube_url",
        ]
