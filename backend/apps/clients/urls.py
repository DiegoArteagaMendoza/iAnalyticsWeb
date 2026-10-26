from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.clients.views import CertificationViewSet, ClientsSectionManagementView, ClientViewSet, TestimonialViewSet

router = SimpleRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("testimonials", TestimonialViewSet, basename="testimonial")
router.register("certifications", CertificationViewSet, basename="certification")

urlpatterns = [
    path("clients_section/", ClientsSectionManagementView.as_view(), name="clients_section"),
    *router.urls,
]
