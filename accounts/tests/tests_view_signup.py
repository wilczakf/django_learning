from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from accounts.views import signup
from accounts.forms import SignUpForm


class SignUpTests(TestCase):
    def setUp(self) -> None:
        url = reverse("signup")
        self.response = self.client.get(url)

    def test__signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__signup_url_resolves_signup_view(self):
        view = resolve("/signup/")
        self.assertEqual(view.func, signup)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, SignUpForm)

    def test__form_inputs(self):
        """
        The view must contain five inputs: `csrf`, `username`, `email`,
        `password1`, `password2`.
        """
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignupTests(TestCase):
    def setUp(self) -> None:
        url = reverse("signup")
        data = {
            "username": "test_user",
            "email": "user@test.com",
            "password1": "test_password",
            "password2": "test_password",
        }

        self.response = self.client.post(url, data)
        self.home_url = reverse("home")

    def test__redirect_to_home(self):
        """Valid form submission should redirect the user to home page."""
        self.assertRedirects(self.response, self.home_url)

    def test__user_creation(self):
        self.assertTrue(User.objects.exists())

    def test__user_authentication(self):
        """
        Create a new request to an arbitrary page.
        Resulting response should now have a `user` to its context,
        after a successful sign-up.
        """
        response = self.client.get(self.home_url)
        user = response.context.get("user")
        self.assertTrue(user.is_authenticated)


class InvalidSignupTests(TestCase):
    def setUp(self) -> None:
        url = reverse("signup")
        data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        self.response = self.client.post(url, data)

    def test__signup_status_code(self):
        """Invalid form submission should return the same page."""
        self.assertEqual(self.response.status_code, 200)

    def test__form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)

    def test__dont_create_user(self):
        self.assertFalse(User.objects.exists())
