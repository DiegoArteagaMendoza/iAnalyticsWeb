"""Proveedores de traducción automática. Se elige uno con TRANSLATION_PROVIDER."""
import requests
from django.conf import settings


class TranslationError(Exception):
    pass


class BaseTranslationProvider:
    name = "base"

    def translate(self, text, source_language, target_language):
        raise NotImplementedError


class NoTranslationProvider(BaseTranslationProvider):
    """No traduce: el texto en inglés queda vacío hasta que alguien lo escriba."""

    name = "none"

    def translate(self, text, source_language, target_language):
        return None


class DeeplTranslationProvider(BaseTranslationProvider):
    name = "deepl"

    def translate(self, text, source_language, target_language):
        if not settings.DEEPL_API_KEY:
            raise TranslationError("Falta configurar DEEPL_API_KEY.")
        target = "EN-US" if target_language == "en" else target_language.upper()
        try:
            response = requests.post(
                settings.DEEPL_API_URL,
                headers={"Authorization": f"DeepL-Auth-Key {settings.DEEPL_API_KEY}"},
                data={"text": text, "source_lang": source_language.upper(), "target_lang": target},
                timeout=settings.TRANSLATION_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()["translations"][0]["text"]
        except (requests.RequestException, KeyError, IndexError, ValueError) as error:
            raise TranslationError(f"DeepL no respondió correctamente: {error}") from error


class LibretranslateTranslationProvider(BaseTranslationProvider):
    name = "libretranslate"

    def translate(self, text, source_language, target_language):
        payload = {"q": text, "source": source_language, "target": target_language, "format": "text"}
        if settings.LIBRETRANSLATE_API_KEY:
            payload["api_key"] = settings.LIBRETRANSLATE_API_KEY
        try:
            response = requests.post(
                settings.LIBRETRANSLATE_URL,
                json=payload,
                timeout=settings.TRANSLATION_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()["translatedText"]
        except (requests.RequestException, KeyError, ValueError) as error:
            raise TranslationError(f"LibreTranslate no respondió correctamente: {error}") from error


PROVIDERS = {
    provider.name: provider
    for provider in (NoTranslationProvider, DeeplTranslationProvider, LibretranslateTranslationProvider)
}
