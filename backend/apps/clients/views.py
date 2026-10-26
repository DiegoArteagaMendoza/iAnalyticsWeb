from apps.clients.models import Certification, Client, Testimonial
from apps.clients.serializers import (
    CertificationManagementSerializer,
    ClientManagementSerializer,
    ClientsSectionManagementSerializer,
    TestimonialManagementSerializer,
)
from apps.core.views import ManagementViewSet, SingletonManagementView


class ClientsSectionManagementView(SingletonManagementView):
    serializer_class = ClientsSectionManagementSerializer


class ClientViewSet(ManagementViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientManagementSerializer


class TestimonialViewSet(ManagementViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialManagementSerializer


class CertificationViewSet(ManagementViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationManagementSerializer
