from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.core.test_utils import TemporaryMediaMixin, make_png, make_staff_user
from apps.media_library.models import MediaFile


@mock.patch("apps.core.translation.services.translate_text", return_value=None)
class MediaLibraryTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_staff_user()
        self.client.force_authenticate(self.user)

    def upload(self, uploaded_file, title="Banner"):
        return self.client.post("/api/v1/media_files/", {"title": title, "file": uploaded_file}, format="multipart")

    def test_upload_image(self, translate):
        response = self.upload(make_png("banner.png"))

        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertTrue(data["is_image"])
        self.assertEqual(data["content_type"], "image/png")
        self.assertGreater(data["size_bytes"], 0)
        self.assertEqual(data["uploaded_by"], self.user.username)

    def test_download_returns_the_file_as_attachment(self, translate):
        media_id = self.upload(make_png("banner.png")).json()["id"]

        response = self.client.get(f"/api/v1/media_files/{media_id}/download/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("banner", response["Content-Disposition"])
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\x89PNG"))

    def test_delete_removes_the_file_from_disk(self, translate):
        media_id = self.upload(make_png("borrar.png")).json()["id"]
        path = Path(MediaFile.objects.get(pk=media_id).file.path)

        self.assertEqual(self.client.delete(f"/api/v1/media_files/{media_id}/").status_code, 204)
        self.assertFalse(path.exists())

    def test_rejects_disallowed_extensions(self, translate):
        script = SimpleUploadedFile("ataque.html", b"<script>alert(1)</script>", content_type="text/html")
        self.assertEqual(self.upload(script).status_code, 400)

    @override_settings(MAX_UPLOAD_SIZE_MB=0)
    def test_rejects_files_over_the_size_limit(self, translate):
        self.assertEqual(self.upload(make_png("grande.png")).status_code, 400)

    def test_search(self, translate):
        self.upload(make_png("a.png"), title="Logo cliente")
        self.upload(make_png("b.png"), title="Foto equipo")
        results = self.client.get("/api/v1/media_files/?search=cliente").json()["results"]
        self.assertEqual([item["title"] for item in results], ["Logo cliente"])
