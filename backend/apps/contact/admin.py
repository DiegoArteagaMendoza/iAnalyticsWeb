from django.contrib import admin

from apps.contact.models import ContactMessage, ContactSection
from apps.core.admin import SingletonAdmin


@admin.register(ContactSection)
class ContactSectionAdmin(SingletonAdmin):
    pass


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["full_name", "company", "email", "service_of_interest", "is_read", "created_at"]
    list_filter = ["is_read", "service_of_interest", "language"]
    list_editable = ["is_read"]
    search_fields = ["full_name", "company", "email", "message"]
    readonly_fields = [
        "full_name",
        "company",
        "email",
        "phone",
        "service_of_interest",
        "message",
        "language",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False
