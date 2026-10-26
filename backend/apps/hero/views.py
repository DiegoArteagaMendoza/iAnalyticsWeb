from apps.core.views import ManagementViewSet, SingletonManagementView
from apps.hero.models import HeroHighlight
from apps.hero.serializers import HeroHighlightManagementSerializer, HeroSectionManagementSerializer


class HeroSectionManagementView(SingletonManagementView):
    serializer_class = HeroSectionManagementSerializer


class HeroHighlightViewSet(ManagementViewSet):
    queryset = HeroHighlight.objects.all()
    serializer_class = HeroHighlightManagementSerializer
