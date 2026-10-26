from io import StringIO
from unittest import mock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.about.models import AboutSection
from apps.core.test_utils import TemporaryMediaMixin
from apps.services.models import Service
from apps.team.models import TeamMember


@mock.patch("apps.core.translation.services.translate_text", return_value=None)
class PageContentTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        cache.clear()
        call_command("load_initial_content", stdout=StringIO())
        self.client = APIClient()

    def get_page(self, language=None):
        url = "/api/v1/page_content/" + (f"?lang={language}" if language else "")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_spanish_is_the_default(self, translate):
        page = self.get_page()
        self.assertEqual(page["language"], "es")
        self.assertEqual(page["hero"]["title_line_1"], "No solo desarrollamos software.")

    def test_english_version(self, translate):
        page = self.get_page("en")
        self.assertEqual(page["hero"]["title_line_2"], "We build solutions that work.")
        self.assertEqual(page["services"]["items"][1]["title"], "Consulting")
        self.assertEqual(page["site_settings"]["business_hours"], "Monday to Friday, 9:00 a.m. to 6:00 p.m.")

    def test_unknown_language_falls_back_to_spanish(self, translate):
        self.assertEqual(self.get_page("fr")["language"], "es")

    def test_missing_english_falls_back_to_spanish(self, translate):
        service = Service.objects.first()
        service.title_en = ""
        service.save()
        self.assertEqual(self.get_page("en")["services"]["items"][0]["title"], service.title_es)

    def test_public_output_has_no_internal_fields(self, translate):
        hero = self.get_page()["hero"]
        self.assertNotIn("title_line_1_es", hero)
        self.assertNotIn("auto_translations", hero)

    def test_only_published_items_are_listed(self, translate):
        self.assertEqual(self.get_page()["team"]["founders"], [])
        TeamMember.objects.filter(is_founder=True).update(is_published=True)
        self.assertEqual(len(self.get_page()["team"]["founders"]), 2)

    def test_hidden_section_is_null(self, translate):
        about = AboutSection.load()
        about.is_visible = False
        about.save()
        self.assertIsNone(self.get_page()["about"])

    def test_initial_content_includes_brand_images(self, translate):
        site_settings = self.get_page()["site_settings"]
        self.assertTrue(site_settings["logo_mark"].endswith(".png"))
        self.assertTrue(site_settings["favicon"].endswith(".png"))

    def test_preview_includes_unpublished_items_for_staff(self, translate):
        from apps.core.test_utils import make_staff_user

        about = AboutSection.load()
        about.is_visible = False
        about.save()
        self.client.force_authenticate(make_staff_user())

        page = self.client.get("/api/v1/page_content/?preview=1").json()

        self.assertTrue(page["is_preview"])
        self.assertEqual(len(page["team"]["founders"]), 2)
        self.assertFalse(page["team"]["founders"][0]["is_published"])
        self.assertFalse(page["about"]["is_visible"])

    def test_preview_is_ignored_for_visitors(self, translate):
        page = self.client.get("/api/v1/page_content/?preview=1").json()
        self.assertFalse(page["is_preview"])
        self.assertEqual(page["team"]["founders"], [])

    def test_initial_content_is_not_loaded_twice(self, translate):
        output = StringIO()
        call_command("load_initial_content", stdout=output)
        self.assertIn("--reset", output.getvalue())
        self.assertEqual(Service.objects.count(), 3)
