from django.contrib.auth.models import User
from django.test import TestCase
from django.forms import ModelForm
from django.urls import reverse, resolve
from boards.models import Board, Post, Topic
from boards.views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(
            name="Heheszki", description="All the heheszki."
        )
        self.username = "test_user"
        self.email = "user@test.com"
        self.password = "test_password_123"
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.topic = Topic.objects.create(
            subject="Hej", board=self.board, starting_user=user
        )
        self.post = Post.objects.create(
            message="Jesteście cali?", topic=self.topic, created_by=user
        )
        self.url = reverse(
            "edit_post",
            kwargs={
                "board_pk": self.board.pk,
                "topic_pk": self.topic.pk,
                "post_pk": self.post.pk,
            },
        )


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test__redirect(self):
        """Test if only logged-in users can edit the posts."""
        login_url = reverse("login")
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self) -> None:
        """Override user creation with different from the one who posted"""
        super().setUp()
        username = "walczak"
        email = "walczak@walczak.com"
        password = "walczak_jest_super_123"
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test__status_code(self):
        """
        Topic can be edited only by its creator.
        Unauthorized users should get a 404 response status code.

        """
        self.assertEqual(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self) -> None:
        """Logs in the current user - post creator."""
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_class(self):
        view = resolve("/boards/1/topics/1/posts/1/edit/")
        self.assertEqual(view.func.view_class, PostUpdateView)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, ModelForm)

    def test__form_inputs(self):
        """The view must contain two inputs: csrf, message textarea."""
        self.assertContains(self.response, "<input", 1)
        self.assertContains(self.response, "<textarea", 1)


class SuccessfulPostUpdateView(PostUpdateViewTestCase):
    def setUp(self) -> None:
        """Logs in the current user - post creator."""
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.edited_message = "edited_message"
        self.response = self.client.post(self.url, {"message": self.edited_message})

    def test__redirect(self):
        """Valid form submission shall redirect the user to current topic posts page."""
        topic_posts_url = reverse(
            "topic_posts", kwargs={"board_pk": self.board.pk, "topic_pk": self.topic.pk}
        )
        self.assertRedirects(self.response, topic_posts_url)

    def test__post_changed(self):
        self.post.refresh_from_db()
        self.assertEqual(self.post.message, self.edited_message)


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self) -> None:
        """Submit empty dict to the `reply_topic` view."""
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test__status_code(self):
        """Invalid form submission shall return to the same page (200 OK)."""
        self.assertEqual(self.response.status_code, 200)

    def test__form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)
