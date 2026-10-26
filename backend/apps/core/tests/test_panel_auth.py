from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.core.test_utils import make_staff_user

PASSWORD = "clave-segura-123"


class PanelAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = make_staff_user("editora@ianalytics.cl")

    def login(self, username="editora@ianalytics.cl", password=PASSWORD):
        return self.client.post("/api/v1/auth/login/", {"username": username, "password": password}, format="json")

    def test_login_returns_token_and_user(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "editora@ianalytics.cl")
        self.assertTrue(response.json()["user"]["is_superuser"])
        self.assertEqual(Token.objects.get(user=self.user).key, response.json()["token"])

    def test_wrong_password_is_rejected(self):
        self.assertEqual(self.login(password="incorrecta").status_code, 400)

    def test_non_staff_users_cannot_log_in(self):
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(self.login().status_code, 400)

    def test_login_rotates_the_token(self):
        first = self.login().json()["token"]
        second = self.login().json()["token"]
        self.assertNotEqual(first, second)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {first}")
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)

    def test_me_and_logout(self):
        token = self.login().json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(self.client.get("/api/v1/auth/me/").json()["username"], "editora@ianalytics.cl")

        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 204)
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)

    @override_settings(TOKEN_TTL_HOURS=12)
    def test_expired_tokens_are_rejected_and_deleted(self):
        token = self.login().json()["token"]
        Token.objects.filter(key=token).update(created=timezone.now() - timedelta(hours=13))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)
        self.assertFalse(Token.objects.filter(key=token).exists())

    def test_staff_users_list(self):
        make_staff_user("otro", superuser=False)
        self.client.force_authenticate(self.user)
        usernames = [user["username"] for user in self.client.get("/api/v1/auth/staff_users/").json()]
        self.assertEqual(usernames, ["editora@ianalytics.cl", "otro"])

    def test_staff_users_requires_staff(self):
        self.assertEqual(self.client.get("/api/v1/auth/staff_users/").status_code, 401)
