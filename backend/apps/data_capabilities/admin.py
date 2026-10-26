from django.contrib import admin

from apps.core.admin import OrderedAdmin, SingletonAdmin
from apps.data_capabilities.models import DataCapabilitiesSection, DataCapability


@admin.register(DataCapabilitiesSection)
class DataCapabilitiesSectionAdmin(SingletonAdmin):
    pass


@admin.register(DataCapability)
class DataCapabilityAdmin(OrderedAdmin):
    list_display = ["title_es", "title_en", "order", "is_published"]
