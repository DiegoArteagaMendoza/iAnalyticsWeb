import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from apps.core.translation.providers import PROVIDERS, TranslationError

logger = logging.getLogger(__name__)


def get_provider():
    provider_class = PROVIDERS.get(settings.TRANSLATION_PROVIDER)
    if provider_class is None:
        raise ImproperlyConfigured(
            f"TRANSLATION_PROVIDER='{settings.TRANSLATION_PROVIDER}' no es válido. "
            f"Opciones: {', '.join(PROVIDERS)}."
        )
    return provider_class()


def translate_text(text, source_language, target_language):
    """
    Traduce un texto. Devuelve None si no hay proveedor o si la traducción falla:
    un error del servicio externo nunca impide guardar el contenido.
    """
    if not text or not text.strip():
        return text
    try:
        return get_provider().translate(text, source_language, target_language)
    except TranslationError as error:
        logger.warning("Traducción automática fallida (%s → %s): %s", source_language, target_language, error)
        return None
