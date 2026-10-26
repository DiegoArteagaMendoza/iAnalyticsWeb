from unittest import mock

from django.test import TestCase, override_settings

from apps.core.translation import services
from apps.core.translation.providers import TranslationError
from apps.hero.models import HeroHighlight


def fake_translate(text, source_language, target_language):
    return f"[{target_language}] {text}"


TRANSLATE_PATH = "apps.core.translation.services.translate_text"


class AutoTranslationTests(TestCase):
    @mock.patch(TRANSLATE_PATH, side_effect=fake_translate)
    def test_empty_english_is_translated_on_save(self, translate):
        highlight = HeroHighlight.objects.create(text_es="Inteligencia de Negocios")

        self.assertEqual(highlight.text_en, "[en] Inteligencia de Negocios")
        translate.assert_called_once_with("Inteligencia de Negocios", "es", "en")

    @mock.patch(TRANSLATE_PATH, side_effect=fake_translate)
    def test_auto_translation_follows_spanish_changes(self, translate):
        highlight = HeroHighlight.objects.create(text_es="Datos")
        highlight.text_es = "Datos e inteligencia"
        highlight.save()

        highlight.refresh_from_db()
        self.assertEqual(highlight.text_en, "[en] Datos e inteligencia")

    @mock.patch(TRANSLATE_PATH, side_effect=fake_translate)
    def test_manual_english_is_never_overwritten(self, translate):
        highlight = HeroHighlight.objects.create(text_es="Datos")
        highlight.text_en = "Data (manual)"
        highlight.save()
        highlight.text_es = "Datos nuevos"
        highlight.save()

        highlight.refresh_from_db()
        self.assertEqual(highlight.text_en, "Data (manual)")

    @mock.patch(TRANSLATE_PATH, side_effect=fake_translate)
    def test_unchanged_spanish_does_not_call_the_service_again(self, translate):
        highlight = HeroHighlight.objects.create(text_es="Datos")
        highlight.order = 3
        highlight.save()

        self.assertEqual(translate.call_count, 1)

    @mock.patch(TRANSLATE_PATH, return_value=None)
    def test_failed_translation_still_saves(self, translate):
        highlight = HeroHighlight.objects.create(text_es="Datos")

        highlight.refresh_from_db()
        self.assertEqual(highlight.text_es, "Datos")
        self.assertEqual(highlight.text_en, "")
        self.assertEqual(highlight.get_translation("text", "en"), "Datos")

    @override_settings(TRANSLATION_PROVIDER="deepl", DEEPL_API_KEY="")
    def test_provider_error_returns_none(self):
        self.assertIsNone(services.translate_text("Hola", "es", "en"))

    @override_settings(TRANSLATION_PROVIDER="deepl", DEEPL_API_KEY="clave")
    def test_deepl_provider_parses_response(self):
        response = mock.Mock()
        response.json.return_value = {"translations": [{"text": "Hello"}]}
        with mock.patch("apps.core.translation.providers.requests.post", return_value=response) as post:
            self.assertEqual(services.translate_text("Hola", "es", "en"), "Hello")
        self.assertEqual(post.call_args.kwargs["data"]["target_lang"], "EN-US")

    def test_provider_error_class_is_handled(self):
        with mock.patch.object(services, "get_provider") as get_provider:
            get_provider.return_value.translate.side_effect = TranslationError("caído")
            self.assertIsNone(services.translate_text("Hola", "es", "en"))
