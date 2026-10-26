"""
Configuración del backend de iAnalytics.

Todos los valores sensibles o dependientes del entorno se leen desde variables
de entorno (o desde un archivo .env en la carpeta backend/). Ver .env.example.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# --- Seguridad -------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me" if DEBUG else None)
# localhost se agrega siempre para el healthcheck del contenedor; DJANGO_INTERNAL_HOSTS
# son los nombres con que otros contenedores llaman al backend (ej: "backend" desde el frontend)
ALLOWED_HOSTS = list(
    dict.fromkeys(
        [
            *env.list("DJANGO_ALLOWED_HOSTS", default=[]),
            *env.list("DJANGO_INTERNAL_HOSTS", default=[]),
            "localhost",
            "127.0.0.1",
        ]
    )
)
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

if not DEBUG:
    SESSION_COOKIE_SECURE = env.bool("DJANGO_SECURE_COOKIES", default=True)
    CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    # Activar cuando el sitio se sirva solo por HTTPS (normalmente detrás del proxy de Docker)
    SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
    SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0

# --- Aplicaciones ----------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
]
# Una app por sección de la página
LOCAL_APPS = [
    "apps.core",
    "apps.site_settings",
    "apps.hero",
    "apps.about",
    "apps.team",
    "apps.services",
    "apps.data_capabilities",
    "apps.technologies",
    "apps.clients",
    "apps.contact",
    "apps.media_library",
    "apps.page_content",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos ---------------------------------------------------------
# Por defecto SQLite para desarrollo; en Docker se usa MySQL mediante DATABASE_URL
# (ej: mysql://ianalytics:clave@database:3306/ianalytics).
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"].setdefault("OPTIONS", {}).update(
        {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    )
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Idioma y zona horaria ------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# Idiomas del contenido de la página: el primero es el idioma fuente
CONTENT_LANGUAGES = ["es", "en"]
CONTENT_SOURCE_LANGUAGE = "es"

# --- Archivos estáticos y subidos -----------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = env.path("DJANGO_STATIC_ROOT", default=BASE_DIR / "staticfiles")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = env.path("DJANGO_MEDIA_ROOT", default=BASE_DIR / "media")
# Sirve los archivos subidos desde Django. Útil en un despliegue simple con Docker;
# con mucho tráfico conviene servirlos con un proxy (nginx) o un almacenamiento externo.
SERVE_MEDIA = env.bool("DJANGO_SERVE_MEDIA", default=DEBUG)

MAX_UPLOAD_SIZE_MB = env.int("MAX_UPLOAD_SIZE_MB", default=5)
DATA_UPLOAD_MAX_MEMORY_SIZE = (MAX_UPLOAD_SIZE_MB + 1) * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

# --- Traducción automática -------------------------------------------------
# none: no traduce (el texto en inglés se escribe a mano)
# deepl: API oficial de DeepL (requiere DEEPL_API_KEY; existe plan gratuito)
# libretranslate: servidor LibreTranslate (puede alojarse en Docker)
TRANSLATION_PROVIDER = env("TRANSLATION_PROVIDER", default="none")
TRANSLATION_TIMEOUT_SECONDS = env.int("TRANSLATION_TIMEOUT_SECONDS", default=10)
DEEPL_API_KEY = env("DEEPL_API_KEY", default="")
DEEPL_API_URL = env("DEEPL_API_URL", default="https://api-free.deepl.com/v2/translate")
LIBRETRANSLATE_URL = env("LIBRETRANSLATE_URL", default="http://localhost:5000/translate")
LIBRETRANSLATE_API_KEY = env("LIBRETRANSLATE_API_KEY", default="")

# --- Correo (avisos de mensajes de contacto) ---------------------------------
# Ejemplo SMTP: EMAIL_URL=smtp+tls://usuario:clave@smtp.servidor.cl:587
vars().update(env.email_url("EMAIL_URL", default="consolemail://"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@ianalytics.cl")
CONTACT_NOTIFICATION_EMAILS = env.list("CONTACT_NOTIFICATION_EMAILS", default=[])

# --- Django REST framework -------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.ExpiringTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["apps.core.permissions.IsStaffWithModelPermissions"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "contact_messages": env("CONTACT_THROTTLE_RATE", default="5/hour"),
        "page_content": env("PAGE_CONTENT_THROTTLE_RATE", default="120/minute"),
        "panel_login": env("PANEL_LOGIN_THROTTLE_RATE", default="10/minute"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "iAnalytics API",
    "DESCRIPTION": "API de gestión de contenido del sitio de Informatic Analytics.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# Horas de validez de una sesión del panel (token de la API)
TOKEN_TTL_HOURS = env.int("TOKEN_TTL_HOURS", default=12)

# --- Frontend ----------------------------------------------------------------
# Dirección pública del sitio (enlace "Ver el sitio" del admin)
FRONTEND_PUBLIC_URL = env("FRONTEND_PUBLIC_URL", default="http://localhost:4321/")

# --- CORS (frontend) -------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS

# --- Logs --------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},
}
