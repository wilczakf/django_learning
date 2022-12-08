from django.test import TestCase
from django.urls import reverse, resolve
from boards.views import board_topics
from boards.models import Board


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
