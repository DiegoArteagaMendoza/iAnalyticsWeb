from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.auth_views import LoginView, LogoutView, MeView, StaffUsersView
from apps.core.views import HealthView

admin.site.site_header = "iAnalytics · Gestión del sitio"
admin.site.site_title = "iAnalytics"
admin.site.index_title = "Contenido de la página"
admin.site.site_url = settings.FRONTEND_PUBLIC_URL  # enlace "Ver el sitio" del admin

api_v1_patterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("auth/token/", LoginView.as_view(), name="auth_token"),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path("auth/me/", MeView.as_view(), name="auth_me"),
    path("auth/staff_users/", StaffUsersView.as_view(), name="auth_staff_users"),
    path("", include("apps.page_content.urls")),
    path("", include("apps.site_settings.urls")),
    path("", include("apps.hero.urls")),
    path("", include("apps.about.urls")),
    path("", include("apps.team.urls")),
    path("", include("apps.services.urls")),
    path("", include("apps.data_capabilities.urls")),
    path("", include("apps.technologies.urls")),
    path("", include("apps.clients.urls")),
    path("", include("apps.contact.urls")),
    path("", include("apps.media_library.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger_ui"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(rf"^{settings.MEDIA_URL.strip('/')}/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
