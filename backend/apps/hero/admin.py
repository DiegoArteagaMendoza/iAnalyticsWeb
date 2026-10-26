from django.contrib import admin

from apps.core.admin import OrderedAdmin, SingletonAdmin
from apps.hero.models import HeroHighlight, HeroSection


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    pass


@admin.register(HeroHighlight)
class HeroHighlightAdmin(OrderedAdmin):
    list_display = ["text_es", "text_en", "accent_color", "order", "is_published"]
