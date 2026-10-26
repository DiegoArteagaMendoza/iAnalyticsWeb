from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.about.views import AboutSectionManagementView, CompanyValueViewSet

router = SimpleRouter()
router.register("company_values", CompanyValueViewSet, basename="company_value")

urlpatterns = [
    path("about_section/", AboutSectionManagementView.as_view(), name="about_section"),
    *router.urls,
]
