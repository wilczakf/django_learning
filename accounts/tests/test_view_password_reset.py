from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase


class PasswordResetTests(TestCase):
    def setUp(self) -> None:
        url = reverse("password_reset")
        self.response = self.client.get(url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_function(self):
        view = resolve("/reset/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetView)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, PasswordResetForm)

    def test__form_inputs(self):
        """View must contain both csrf and email inputs."""
        self.assertContains(self.response, "<input", 2)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self) -> None:
        email = "user@test.com"
        User.objects.create_user(
            username="test_user", email=email, password="test_pass_123"
        )
        url = reverse("password_reset")
        self.response = self.client.post(url, {"email": email})

    def test__redirect(self):
        """Valid form submission should redirect user to `password_reset_done` view."""
        url = reverse("password_reset_done")
        self.assertRedirects(self.response, url)

    def test__send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
    def setUp(self) -> None:
        url = reverse("password_reset")
        self.response = self.client.post(url, {"email": "usernotexists@test.com"})

    def test__redirect(self):
        """Invalid email input should redirect user to `password_reset_done` view."""
        url = reverse("password_reset_done")
        self.assertRedirects(self.response, url)

    def test__no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self) -> None:
        url = reverse("password_reset_done")
        self.response = self.client.get(url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_function(self):
        view = resolve("/reset/done/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):
    def setUp(self) -> None:
        """
        Create a user and a valid password reset token
        based on how django creates the token internally.

        """
        user = User.objects.create_user(username="test_user", email="user@test.com", password="test_password_123")
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse("password_reset_confirm", kwargs={
            "uidb64": self.uid,
            "token": self.token
        })
        self.response = self.client.get(url, follow=True)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_function(self):
        view = resolve(f"/reset/{self.uid}/{self.token}/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, SetPasswordForm)

    def test__form_inputs(self):
        """View must contain inputs: csrf and two password fields."""
        self.assertContains(self.response, "<input", 3)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self) -> None:
        """Create test user, invalidate the token by changing the password."""
        user = User.objects.create_user(username="test_user", email="user@test.com", password="test_password_123")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        user.set_password("invalid_pass_123")
        user.save()

        url = reverse("password_reset_confirm", kwargs={
            "uidb64": uid,
            "token": token
        })
        self.response = self.client.get(url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__html(self):
        password_reset_url = reverse("password_reset")
        self.assertContains(self.response, "invalid password reset link")
        self.assertContains(self.response, f'href="{password_reset_url}"')


class PasswordResetCompleteTests(TestCase):
    def setUp(self) -> None:
        url = reverse("password_reset_complete")
        self.response = self.client.get(url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_function(self):
        view = resolve("/reset/complete/")
        self.assertEqual(view.func.view_class, auth_views.PasswordResetCompleteView)