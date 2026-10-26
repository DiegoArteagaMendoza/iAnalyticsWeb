from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.data_capabilities.views import DataCapabilitiesSectionManagementView, DataCapabilityViewSet

router = SimpleRouter()
router.register("data_capabilities", DataCapabilityViewSet, basename="data_capability")

urlpatterns = [
    path("data_capabilities_section/", DataCapabilitiesSectionManagementView.as_view(), name="data_capabilities_section"),
    *router.urls,
]
