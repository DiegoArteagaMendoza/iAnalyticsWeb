from rest_framework import serializers

from apps.core.serializers import LocalizedModelSerializer, management_serializer_for
from apps.team.models import TeamMember, TeamSection

TeamSectionManagementSerializer = management_serializer_for(TeamSection)
TeamMemberManagementSerializer = management_serializer_for(TeamMember)


class TeamMemberPublicSerializer(LocalizedModelSerializer):
    initials = serializers.CharField(read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "order", "is_published", "full_name", "initials", "photo", "linkedin_url", "is_founder", "accent_color"]


class TeamSectionPublicSerializer(LocalizedModelSerializer):
    class Meta:
        model = TeamSection
        fields = ["cta_url"]
