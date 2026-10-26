from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.services.views import ServiceFeatureViewSet, ServicesSectionManagementView, ServiceViewSet

router = SimpleRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("service_features", ServiceFeatureViewSet, basename="service_feature")

urlpatterns = [
    path("services_section/", ServicesSectionManagementView.as_view(), name="services_section"),
    *router.urls,
]
