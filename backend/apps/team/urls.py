from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.team.views import TeamMemberViewSet, TeamSectionManagementView

router = SimpleRouter()
router.register("team_members", TeamMemberViewSet, basename="team_member")

urlpatterns = [
    path("team_section/", TeamSectionManagementView.as_view(), name="team_section"),
    *router.urls,
]
