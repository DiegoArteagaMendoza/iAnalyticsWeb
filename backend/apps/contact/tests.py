from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.contact.models import ContactMessage
from apps.core.test_utils import make_staff_user

VALID_MESSAGE = {
    "full_name": "María González",
    "company": "Agrícola Ñuble",
    "email": "maria@example.cl",
    "service_of_interest": "Visibilidad de Datos",
    "message": "Quisiera cotizar un Datawarehouse.",
    "language": "es",
}


class ContactMessageTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_visitor_can_send_a_message(self):
        response = self.client.post("/api/v1/contact_messages/", VALID_MESSAGE, format="json")

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(ContactMessage.objects.get().email, "maria@example.cl")

    def test_visitor_cannot_list_messages(self):
        self.client.post("/api/v1/contact_messages/", VALID_MESSAGE, format="json")
        self.assertEqual(self.client.get("/api/v1/contact_messages/").status_code, 401)

    def test_honeypot_blocks_bots(self):
        response = self.client.post(
            "/api/v1/contact_messages/", {**VALID_MESSAGE, "website": "http://spam.example"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactMessage.objects.exists())

    def test_unknown_language_falls_back_to_spanish(self):
        self.client.post("/api/v1/contact_messages/", {**VALID_MESSAGE, "language": "fr"}, format="json")
        self.assertEqual(ContactMessage.objects.get().language, "es")

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_PERMISSION_CLASSES": ["apps.core.permissions.IsStaffWithModelPermissions"],
            "DEFAULT_THROTTLE_RATES": {"contact_messages": "2/hour", "page_content": "100/minute"},
        }
    )
    def test_rate_limit(self):
        from rest_framework.settings import api_settings
        from rest_framework.throttling import SimpleRateThrottle

        original_rates = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES
        try:
            statuses = [
                self.client.post("/api/v1/contact_messages/", VALID_MESSAGE, format="json").status_code
                for _ in range(3)
            ]
        finally:
            SimpleRateThrottle.THROTTLE_RATES = original_rates
        self.assertEqual(statuses, [201, 201, 429])

    @override_settings(CONTACT_NOTIFICATION_EMAILS=["contacto@ianalytics.cl"])
    def test_sends_email_notification(self):
        self.client.post("/api/v1/contact_messages/", VALID_MESSAGE, format="json")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("María González", mail.outbox[0].subject)

    def test_staff_can_mark_as_read_but_not_alter_content(self):
        self.client.post("/api/v1/contact_messages/", VALID_MESSAGE, format="json")
        message_id = ContactMessage.objects.get().pk
        self.client.force_authenticate(make_staff_user())

        response = self.client.patch(
            f"/api/v1/contact_messages/{message_id}/", {"is_read": True, "message": "alterado"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        message = ContactMessage.objects.get()
        self.assertTrue(message.is_read)
        self.assertEqual(message.message, VALID_MESSAGE["message"])
        unread = self.client.get("/api/v1/contact_messages/?is_read=false").json()["results"]
        self.assertEqual(unread, [])
