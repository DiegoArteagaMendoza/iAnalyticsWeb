from apps.clients.models import Certification, Client, ClientsSection, Testimonial
from apps.core.serializers import LocalizedModelSerializer, management_serializer_for

ClientsSectionManagementSerializer = management_serializer_for(ClientsSection)
ClientManagementSerializer = management_serializer_for(Client)
TestimonialManagementSerializer = management_serializer_for(Testimonial)
CertificationManagementSerializer = management_serializer_for(Certification)


class ClientPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "order", "is_published", "name", "logo", "website_url", "accent_color"]


class TestimonialPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "order", "is_published", "author_name", "company_name", "photo"]


class CertificationPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "order", "is_published", "image", "accent_color"]


class ClientsSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = ClientsSection
        fields = ["cta_url"]
