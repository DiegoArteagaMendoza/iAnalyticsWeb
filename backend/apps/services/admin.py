from django.contrib import admin

from apps.core.admin import OrderedAdmin, SingletonAdmin
from apps.services.models import Service, ServiceFeature, ServicesSection


@admin.register(ServicesSection)
class ServicesSectionAdmin(SingletonAdmin):
    pass


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    fields = ["text_es", "text_en", "order"]
    extra = 1


@admin.register(Service)
class ServiceAdmin(OrderedAdmin):
    list_display = ["title_es", "title_en", "accent_color", "order", "is_published"]
    inlines = [ServiceFeatureInline]
