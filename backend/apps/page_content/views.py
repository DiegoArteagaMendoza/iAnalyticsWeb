from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.about.models import AboutSection, CompanyValue
from apps.about.serializers import AboutSectionPublicSerializer, CompanyValuePublicSerializer
from apps.clients.models import Certification, Client, ClientsSection, Testimonial
from apps.clients.serializers import (
    CertificationPublicSerializer,
    ClientPublicSerializer,
    ClientsSectionPublicSerializer,
    TestimonialPublicSerializer,
)
from apps.contact.models import ContactSection
from apps.contact.serializers import ContactSectionPublicSerializer
from apps.data_capabilities.models import DataCapabilitiesSection, DataCapability
from apps.data_capabilities.serializers import DataCapabilitiesSectionPublicSerializer, DataCapabilityPublicSerializer
from apps.hero.models import HeroHighlight, HeroSection
from apps.hero.serializers import HeroHighlightPublicSerializer, HeroSectionPublicSerializer
from apps.services.models import Service, ServicesSection
from apps.services.serializers import ServicePublicSerializer, ServicesSectionPublicSerializer
from apps.site_settings.models import SiteSettings
from apps.site_settings.serializers import SiteSettingsPublicSerializer
from apps.team.models import TeamMember, TeamSection
from apps.team.serializers import TeamMemberPublicSerializer, TeamSectionPublicSerializer
from apps.technologies.models import TechnologiesSection, Technology
from apps.technologies.serializers import TechnologiesSectionPublicSerializer, TechnologyPublicSerializer


def resolve_language(request):
    requested = (request.query_params.get("lang") or "").lower()[:2]
    if requested in settings.CONTENT_LANGUAGES:
        return requested
    return settings.CONTENT_SOURCE_LANGUAGE


class PageContentView(APIView):
    """
    Contenido publicado de toda la página, en el idioma pedido (?lang=es|en).

    Con ?preview=1 y un usuario del staff autenticado (panel de edición) incluye también
    los elementos sin publicar y las secciones ocultas, marcados con is_published / is_visible.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "page_content"

    @extend_schema(
        parameters=[
            OpenApiParameter("lang", OpenApiTypes.STR, enum=settings.CONTENT_LANGUAGES),
            OpenApiParameter("preview", OpenApiTypes.BOOL, description="Solo staff: incluye lo no publicado."),
        ],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        language = resolve_language(request)
        is_preview = request.query_params.get("preview") in ("1", "true") and request.user.is_staff
        context = {"request": request, "language": language}

        def one(serializer_class, instance):
            return serializer_class(instance, context=context).data

        def many(serializer_class, queryset):
            return serializer_class(queryset, many=True, context=context).data

        def section(model, serializer_class, **items):
            instance = model.load()
            if not instance.is_visible and not is_preview:
                return None
            return {**one(serializer_class, instance), "is_visible": instance.is_visible, **items}

        published = {} if is_preview else {"is_published": True}
        services = Service.objects.filter(**published).prefetch_related("features")
        team_members = TeamMember.objects.filter(**published)

        response = Response(
            {
                "language": language,
                "is_preview": is_preview,
                "available_languages": settings.CONTENT_LANGUAGES,
                "site_settings": one(SiteSettingsPublicSerializer, SiteSettings.load()),
                "hero": {
                    **one(HeroSectionPublicSerializer, HeroSection.load()),
                    "highlights": many(HeroHighlightPublicSerializer, HeroHighlight.objects.filter(**published)),
                },
                "about": section(
                    AboutSection,
                    AboutSectionPublicSerializer,
                    values=many(CompanyValuePublicSerializer, CompanyValue.objects.filter(**published)),
                ),
                "team": section(
                    TeamSection,
                    TeamSectionPublicSerializer,
                    founders=many(TeamMemberPublicSerializer, team_members.filter(is_founder=True)),
                    members=many(TeamMemberPublicSerializer, team_members.filter(is_founder=False)),
                ),
                "services": section(
                    ServicesSection,
                    ServicesSectionPublicSerializer,
                    items=many(ServicePublicSerializer, services),
                ),
                "data_capabilities": section(
                    DataCapabilitiesSection,
                    DataCapabilitiesSectionPublicSerializer,
                    items=many(DataCapabilityPublicSerializer, DataCapability.objects.filter(**published)),
                ),
                "technologies": section(
                    TechnologiesSection,
                    TechnologiesSectionPublicSerializer,
                    items=many(TechnologyPublicSerializer, Technology.objects.filter(**published)),
                ),
                "clients": section(
                    ClientsSection,
                    ClientsSectionPublicSerializer,
                    items=many(ClientPublicSerializer, Client.objects.filter(**published)),
                    testimonials=many(TestimonialPublicSerializer, Testimonial.objects.filter(**published)),
                    certifications=many(CertificationPublicSerializer, Certification.objects.filter(**published)),
                ),
                "contact": section(
                    ContactSection,
                    ContactSectionPublicSerializer,
                    service_options=[
                        service.get_translation("title", language) for service in services
                    ],
                ),
            }
        )
        if is_preview:
            response["Cache-Control"] = "no-store"
        return response
