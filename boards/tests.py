from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from boards.views import home, board_topics, new_topic
from boards.models import Board, Topic, Post
from boards.forms import NewTopicForm


class HomeTests(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(
            name="Heheszki", description="All the heheszki."
        )
        url = reverse("home")
        self.response = self.client.get(url)

    def test__home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__home_url_resolves_home_view(self):
        view = resolve("/")
        self.assertEqual(view.func, home)

    def test__home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse("board_topics", kwargs={"board_pk": self.board.pk})
        self.assertContains(self.response, f'href="{board_topics_url}"')


class BoardTopicsTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name="Heheszki", description="All the heheszki.")

    def get_url(self, url: str):
        return self.client.get(url)

    def test__board_topics_view_success_status_code(self):
        url = reverse("board_topics", kwargs={"board_pk": 1})
        response = self.get_url(url)
        self.assertEqual(response.status_code, 200)

    def test__board_topics_view_not_found_status_code(self):
        url = reverse("board_topics", kwargs={"board_pk": 99})
        response = self.get_url(url)
        self.assertEqual(response.status_code, 404)

    def test__board_topics_url_resolves_board_topics_view(self):
        view = resolve("/boards/1/")
        self.assertEqual(view.func, board_topics)

    def test__board_topics_view_contains_nav_links(self):
        board_pk_kwarg = {"board_pk": 1}
        board_topics_url = reverse("board_topics", kwargs=board_pk_kwarg)
        home_url = reverse("home")
        new_topic_url = reverse("new_topic", kwargs=board_pk_kwarg)

        response = self.client.get(board_topics_url)

        self.assertContains(response, f'href="{home_url}"')
        self.assertContains(response, f'href="{new_topic_url}"')


class NewTopicTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name="Heheszki", description="All the heheszki.")
        User.objects.create(username="Walczak", email="walczak@ls.com", password="123")

    def test__new_topic_success_status_code(self):
        url = reverse("new_topic", kwargs={"board_pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test__new_topic_not_found_status_code(self):
        url = reverse("new_topic", kwargs={"board_pk": 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test__new_topic_resolves_new_topic_view(self):
        view = resolve("/boards/1/new/")
        self.assertEqual(view.func, new_topic)

    def test__new_topic_view_contains_link_back_to_board_topics_view(self):
        board_pk_kwarg = {"board_pk": 1}
        new_topic_url = reverse("new_topic", kwargs=board_pk_kwarg)
        board_topics_url = reverse("board_topics", kwargs=board_pk_kwarg)
        response = self.client.get(new_topic_url)
        self.assertContains(response, f'href="{board_topics_url}"')

    def test__csrf(self):
        url = reverse("new_topic", kwargs={"board_pk": 1})
        response = self.client.get(url)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test__contains_form(self):
        url = reverse("new_topic", kwargs={"board_pk": 1})
        response = self.client.get(url)
        form = response.context.get("form")
        self.assertIsInstance(form, NewTopicForm)

    def test__new_topic_valid_post_data(self):
        url = reverse("new_topic", kwargs={"board_pk": 1})
        data = {"subject": "Shitstorm", "message": "You suck."}

        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test__new_topic_invalid_post_data(self):
        """
        Invalid post data should not redirect.
        The expected behaviour is to show the form again with validation errors.
        """

        url = reverse("new_topic", kwargs={"board_pk": 1})
        response = self.client.post(url, {})
        form = response.context.get("form")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)

    def test__new_topic_invalid_post_data_empty_fields(self):
        """
        Invalid post data should not redirect.
        The expected behaviour is to show the form again with validation errors.
        """

        url = reverse("new_topic", kwargs={"board_pk": 1})
        data = {"subject": "", "message": ""}

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())
