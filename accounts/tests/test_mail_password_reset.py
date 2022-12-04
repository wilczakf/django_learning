from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase


class PasswordResetMailTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(
            username="test_user", email="user@test.com", password="test_password_123"
        )
        self.response = self.client.post(
            reverse("password_reset"), {"email": "user@test.com"}
        )
        self.email = mail.outbox[0]

    def test__email_subject(self):
        expected_subject = "[London Spitfire Boards] Reset password submission"
        self.assertEqual(expected_subject, self.email.subject)

    def test__email_body(self):
        context = self.response.context
        token = context.get("token")
        uid = context.get("uid")
        password_reset_token_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )

        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn("user", self.email.body)
        self.assertIn("user@test.com", self.email.body)

    def test__email_to(self):
        self.assertEqual(["user@test.com"], self.email.to)
