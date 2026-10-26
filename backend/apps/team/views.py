from rest_framework import filters

from apps.core.views import ManagementViewSet, SingletonManagementView
from apps.team.models import TeamMember
from apps.team.serializers import TeamMemberManagementSerializer, TeamSectionManagementSerializer


class TeamSectionManagementView(SingletonManagementView):
    serializer_class = TeamSectionManagementSerializer


class TeamMemberViewSet(ManagementViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberManagementSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "role_es", "role_en"]
