from apps.core.views import SingletonManagementView
from apps.site_settings.serializers import SiteSettingsManagementSerializer


class SiteSettingsManagementView(SingletonManagementView):
    serializer_class = SiteSettingsManagementSerializer
