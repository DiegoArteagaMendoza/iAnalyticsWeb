from django.contrib import admin

from apps.core.admin import OrderedAdmin, SingletonAdmin
from apps.technologies.models import TechnologiesSection, Technology


@admin.register(TechnologiesSection)
class TechnologiesSectionAdmin(SingletonAdmin):
    pass


@admin.register(Technology)
class TechnologyAdmin(OrderedAdmin):
    list_display = ["name", "category", "order", "is_published"]
    list_filter = ["category", "is_published"]
