from apps.core.views import ManagementViewSet, SingletonManagementView
from apps.technologies.models import Technology
from apps.technologies.serializers import TechnologiesSectionManagementSerializer, TechnologyManagementSerializer


class TechnologiesSectionManagementView(SingletonManagementView):
    serializer_class = TechnologiesSectionManagementSerializer


class TechnologyViewSet(ManagementViewSet):
    """Tecnologías. Filtrar con ?category=development|data."""

    queryset = Technology.objects.all()
    serializer_class = TechnologyManagementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category in Technology.Category.values:
            queryset = queryset.filter(category=category)
        return queryset
