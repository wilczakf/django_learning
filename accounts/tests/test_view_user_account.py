from django.forms import ModelForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from accounts.views import UserUpdateView


class UserAccountTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "test_user"
        self.email = "user@test.com"
        self.password = "test_password_123"
        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.url = reverse("account")


class UserAccountTests(UserAccountTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__url_resolve_account_view(self):
        view = resolve("/settings/account/")
        self.assertEqual(view.func.view_class, UserUpdateView)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, ModelForm)

    def test__form_input(self):
        """
        View must contain 4 inputs:
            csrf (token)
            first_name (text)
            last_name (text)
            email (email)

        """
        self.assertContains(self.response, "<input", 4)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="email"', 1)


class LoginRequiredUserAccountTests(TestCase):
    def test__redirect(self):
        url = reverse("account")
        login_url = reverse("login")
        response = self.client.get(url)
        self.assertRedirects(response, f"{login_url}?next={url}")


class SuccessfulUpdateUserAccountTests(UserAccountTestCase):
    def setUp(self) -> None:
        super(SuccessfulUpdateUserAccountTests, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.updated_user_data = {
            "first_name": "Filip",
            "last_name": "Walczak",
            "email": "walczak@walczak.com",
        }
        self.response = self.client.post(self.url, self.updated_user_data)

    def test__redirect(self):
        """Valid form submission shall redirect the user to the same page."""
        self.assertRedirects(self.response, self.url)

    def test__user_data_changed(self):
        """User account view should show updated data after refreshing from DB."""
        self.user.refresh_from_db()
        self.assertEqual(self.updated_user_data["first_name"], self.user.first_name)
        self.assertEqual(self.updated_user_data["last_name"], self.user.last_name)
        self.assertEqual(self.updated_user_data["email"], self.user.email)


class InvalidUpdateUserAccountTests(UserAccountTestCase):
    def setUp(self) -> None:
        super(InvalidUpdateUserAccountTests, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {"first_name": "what" * 100})

    def test__status_code(self):
        """Invalid form submission shall return to the same page (200 OK)"""
        self.assertEqual(self.response.status_code, 200)

    def test__form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)
