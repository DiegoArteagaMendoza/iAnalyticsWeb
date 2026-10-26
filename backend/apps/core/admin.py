from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse


class SingletonAdmin(admin.ModelAdmin):
    """Admin para secciones de registro único: se edita directamente, sin listado."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        instance = self.model.load()
        opts = self.model._meta
        return redirect(reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[instance.pk]))


class OrderedAdmin(admin.ModelAdmin):
    list_editable = ["order", "is_published"]
    list_filter = ["is_published"]
