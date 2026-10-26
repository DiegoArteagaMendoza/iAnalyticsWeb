from django.contrib import admin

from apps.core.admin import OrderedAdmin, SingletonAdmin
from apps.team.models import TeamMember, TeamSection


@admin.register(TeamSection)
class TeamSectionAdmin(SingletonAdmin):
    pass


@admin.register(TeamMember)
class TeamMemberAdmin(OrderedAdmin):
    list_display = ["full_name", "role_es", "is_founder", "order", "is_published"]
    list_filter = ["is_founder", "is_published"]
    search_fields = ["full_name", "role_es", "role_en"]
