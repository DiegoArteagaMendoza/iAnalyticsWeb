from pathlib import Path
from unittest import mock

from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.test_utils import TemporaryMediaMixin, make_png, make_staff_user
from apps.site_settings.models import SiteSettings
from apps.team.models import TeamMember


@mock.patch("apps.core.translation.services.translate_text", return_value=None)
class ManagementPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_anonymous_cannot_read_or_edit(self, translate):
        self.assertEqual(self.client.get("/api/v1/hero_section/").status_code, 401)
        self.assertEqual(self.client.patch("/api/v1/hero_section/", {"lead_es": "x"}).status_code, 401)

    def test_non_staff_user_is_rejected(self, translate):
        user = make_staff_user("visitante", superuser=False)
        user.is_staff = False
        user.save()
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get("/api/v1/team_members/").status_code, 403)

    def test_staff_needs_model_permissions(self, translate):
        editor = make_staff_user("editor", superuser=False)
        self.client.force_authenticate(editor)
        self.assertEqual(self.client.get("/api/v1/team_members/").status_code, 403)

        editor.user_permissions.add(Permission.objects.get(codename="view_teammember"))
        editor = type(editor).objects.get(pk=editor.pk)  # Django cachea los permisos en el objeto
        self.client.force_authenticate(editor)
        self.assertEqual(self.client.get("/api/v1/team_members/").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/team_members/", {"full_name": "Ana"}).status_code, 403)

    def test_token_authentication(self, translate):
        make_staff_user("admin")
        response = self.client.post("/api/v1/auth/token/", {"username": "admin", "password": "clave-segura-123"})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.json()['token']}")
        self.assertEqual(self.client.get("/api/v1/hero_section/").status_code, 200)


@mock.patch("apps.core.translation.services.translate_text", return_value=None)
class ManagementEditingTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff_user())

    def test_edit_section_texts(self, translate):
        response = self.client.patch(
            "/api/v1/hero_section/",
            {"title_line_1_es": "Nuevo título", "title_line_1_en": "New title"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title_line_1_es"], "Nuevo título")
        self.assertEqual(response.json()["title_line_1_en"], "New title")

    def test_singleton_cannot_be_duplicated(self, translate):
        self.client.patch("/api/v1/site_settings/", {"email": "a@ianalytics.cl"}, format="json")
        self.client.patch("/api/v1/site_settings/", {"email": "b@ianalytics.cl"}, format="json")
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.load().email, "b@ianalytics.cl")

    def test_create_team_member_with_photo(self, translate):
        response = self.client.post(
            "/api/v1/team_members/",
            {"full_name": "Ana Pérez", "role_es": "Desarrolladora", "is_founder": True, "photo": make_png("ana.png")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.content)
        member = TeamMember.objects.get()
        self.assertTrue(Path(member.photo.path).exists())

    def test_replacing_and_deleting_an_image_removes_old_files(self, translate):
        response = self.client.post(
            "/api/v1/team_members/",
            {"full_name": "Ana", "role_es": "Dev", "photo": make_png("uno.png")},
            format="multipart",
        )
        member_id = response.json()["id"]
        first_path = Path(TeamMember.objects.get().photo.path)

        self.client.patch(f"/api/v1/team_members/{member_id}/", {"photo": make_png("dos.png")}, format="multipart")
        second_path = Path(TeamMember.objects.get().photo.path)
        self.assertFalse(first_path.exists())
        self.assertTrue(second_path.exists())

        self.client.delete(f"/api/v1/team_members/{member_id}/")
        self.assertFalse(second_path.exists())

    def test_image_can_be_removed(self, translate):
        response = self.client.post(
            "/api/v1/team_members/",
            {"full_name": "Ana", "role_es": "Dev", "photo": make_png("ana.png")},
            format="multipart",
        )
        member_id = response.json()["id"]
        photo_path = Path(TeamMember.objects.get().photo.path)

        # Desde el editor: campo vacío en multipart
        response = self.client.patch(f"/api/v1/team_members/{member_id}/", {"photo": ""}, format="multipart")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsNone(response.json()["photo"])
        self.assertFalse(TeamMember.objects.get().photo)
        self.assertFalse(photo_path.exists())

        # También con JSON null
        response = self.client.patch(f"/api/v1/team_members/{member_id}/", {"photo": None}, format="json")
        self.assertEqual(response.status_code, 200, response.content)

    def test_rejects_files_that_are_not_images(self, translate):
        from django.core.files.uploadedfile import SimpleUploadedFile

        fake_image = SimpleUploadedFile("logo.png", b"no soy una imagen", content_type="image/png")
        response = self.client.patch("/api/v1/site_settings/", {"logo_mark": fake_image}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("logo_mark", response.json())
