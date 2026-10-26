from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.technologies.views import TechnologiesSectionManagementView, TechnologyViewSet

router = SimpleRouter()
router.register("technologies", TechnologyViewSet, basename="technology")

urlpatterns = [
    path("technologies_section/", TechnologiesSectionManagementView.as_view(), name="technologies_section"),
    *router.urls,
]
