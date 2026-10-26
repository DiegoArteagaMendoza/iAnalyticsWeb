from django.contrib import admin

from apps.about.models import AboutSection, CompanyValue
from apps.core.admin import OrderedAdmin, SingletonAdmin


@admin.register(AboutSection)
class AboutSectionAdmin(SingletonAdmin):
    pass


@admin.register(CompanyValue)
class CompanyValueAdmin(OrderedAdmin):
    list_display = ["name_es", "name_en", "accent_color", "order", "is_published"]
