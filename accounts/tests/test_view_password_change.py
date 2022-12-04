from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase


class LoginRequiredPasswordChangeTests(TestCase):
    def test__redirect(self):
        """Not logged-in password change request
        shall redirect to login page.

        """
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)

        self.assertRedirects(response, f"{login_url}?next={url}")


class PasswordChangeTestCase(TestCase):
    def setUp(self, data=None) -> None:
        if data is None:
            data = {}
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password="old_password")
        self.url = reverse('password_change')
        self.client.login(username="test_user", password="old_password")
        self.response = self.client.post(self.url, data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self, **kwargs) -> None:
        super().setUp({
            "old_password": "old_password",
            "new_password1": "new_password",
            "new_password2": "new_password",
        })

    def test__redirect(self):
        """Valid form submission shall redirect the user."""
        self.assertRedirects(self.response, reverse("password_change_done"))

    def test__password_changed(self):
        """
        Refresh the user instance from database to get the new password
        hash updated by the change password view.

        """
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password"))

    def test__user_authentication(self):
        """
        Create a new request to an arbitrary page.
        Resulting response should now have an `user` added to context
        after a successful sign-up.

        """
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def test__status_code(self):
        """Invalid form submission shall return to the same page."""
        self.assertEqual(self.response.status_code, 200)

    def test__form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test__not_changed_password(self):
        """
        Refresh the user instance from the database
        to make sure we have the latest data.

        """
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))
