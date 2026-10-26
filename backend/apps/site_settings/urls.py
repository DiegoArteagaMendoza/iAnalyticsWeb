from django.urls import path

from apps.site_settings.views import SiteSettingsManagementView

urlpatterns = [
    path("site_settings/", SiteSettingsManagementView.as_view(), name="site_settings"),
]
