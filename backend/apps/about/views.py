from apps.about.models import CompanyValue
from apps.about.serializers import AboutSectionManagementSerializer, CompanyValueManagementSerializer
from apps.core.views import ManagementViewSet, SingletonManagementView


class AboutSectionManagementView(SingletonManagementView):
    serializer_class = AboutSectionManagementSerializer


class CompanyValueViewSet(ManagementViewSet):
    queryset = CompanyValue.objects.all()
    serializer_class = CompanyValueManagementSerializer
