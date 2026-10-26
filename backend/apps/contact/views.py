from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from apps.contact.models import ContactMessage
from apps.contact.notifications import notify_new_message
from apps.contact.serializers import (
    ContactMessageCreateSerializer,
    ContactMessageManagementSerializer,
    ContactSectionManagementSerializer,
)
from apps.core.views import SingletonManagementView


class ContactSectionManagementView(SingletonManagementView):
    serializer_class = ContactSectionManagementSerializer


class ContactMessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST: público (formulario de la página), con límite de envíos por IP.
    GET / PATCH / DELETE: staff. PATCH solo permite marcar `is_read`.
    Filtrar no leídos con ?is_read=false.
    """

    queryset = ContactMessage.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "company", "email", "message"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "contact_messages"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "create":
            return ContactMessageCreateSerializer
        return ContactMessageManagementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        is_read = self.request.query_params.get("is_read")
        if is_read in ("true", "false"):
            queryset = queryset.filter(is_read=is_read == "true")
        return queryset

    def perform_create(self, serializer):
        notify_new_message(serializer.save())
