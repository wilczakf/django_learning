from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from boards.models import Board, Topic, Post
from boards.forms import PostForm
from boards.views import reply_topic


class ReplyTopicTestCase(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(name="Heheszki", description="All the heheszki.")
        self.username = "test_user"
        self.email = "user@test.com"
        self.password = "test_password_123"
        user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.topic = Topic.objects.create(subject="Hello", board=self.board, starting_user=user)
        Post.objects.create(message="Jestescie cali?", topic=self.topic, created_by=user)
        self.url = reverse("reply_topic", kwargs={"board_pk": self.board.pk, "topic_pk": self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test__redirect(self):
        login_url = reverse("login")
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test__resolve_view_fn(self):
        view = resolve("/boards/1/topics/1/reply/")
        self.assertEqual(view.func, reply_topic)

    def test__contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, PostForm)

    def test__form_inputs(self):
        self.assertContains(self.response, "<input", 1)
        self.assertContains(self.response, "<textarea", 1)


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {"message": "jestesmy cali!"})

    def test__redirect(self):
        """Valid form submission shall redirect the user to topic posts page."""
        topic_posts_url = reverse("topic_posts", kwargs={"board_pk": self.board.pk, "topic_pk": self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    def test__reply_created(self):
        """
        Using the test case plus creating new
        total post count shall be 2.

        """
        self.assertEqual(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self) -> None:
        """Submits empty dict (form data) to `reply_topic` view."""
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test__status_code(self):
        """Shall return to the same page."""
        self.assertEqual(self.response.status_code, 200)

    def test__form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)
