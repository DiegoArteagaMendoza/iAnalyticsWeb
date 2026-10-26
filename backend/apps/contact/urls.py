from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.contact.views import ContactMessageViewSet, ContactSectionManagementView

router = SimpleRouter()
router.register("contact_messages", ContactMessageViewSet, basename="contact_message")

urlpatterns = [
    path("contact_section/", ContactSectionManagementView.as_view(), name="contact_section"),
    *router.urls,
]
