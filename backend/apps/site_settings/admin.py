from django.contrib import admin

from apps.core.admin import SingletonAdmin
from apps.site_settings.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = [
        ("Identidad", {"fields": ["company_name", "logo_mark", "logo_wordmark", "logo_wordmark_light", "logo_full", "favicon"]}),
        ("SEO", {"fields": ["meta_title_es", "meta_title_en", "meta_description_es", "meta_description_en"]}),
        (
            "Contacto",
            {
                "fields": [
                    "phone_display",
                    "phone_link",
                    "email",
                    "address",
                    "maps_url",
                    "business_hours_es",
                    "business_hours_en",
                ]
            },
        ),
        (
            "Footer",
            {"fields": ["footer_tagline_es", "footer_tagline_en", "translation_notice_es", "translation_notice_en"]},
        ),
        ("Redes sociales", {"fields": ["linkedin_url", "facebook_url", "instagram_url", "youtube_url"]}),
    ]
