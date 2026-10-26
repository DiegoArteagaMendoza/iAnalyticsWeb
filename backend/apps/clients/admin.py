from django.contrib import admin

from apps.clients.models import Certification, Client, ClientsSection, Testimonial
from apps.core.admin import OrderedAdmin, SingletonAdmin


@admin.register(ClientsSection)
class ClientsSectionAdmin(SingletonAdmin):
    pass


@admin.register(Client)
class ClientAdmin(OrderedAdmin):
    list_display = ["name", "website_url", "order", "is_published"]
    search_fields = ["name"]


@admin.register(Testimonial)
class TestimonialAdmin(OrderedAdmin):
    list_display = ["author_name", "company_name", "order", "is_published"]


@admin.register(Certification)
class CertificationAdmin(OrderedAdmin):
    list_display = ["title_es", "badge_text_es", "order", "is_published"]
