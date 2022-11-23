from django.test import TestCase
from django.urls import reverse, resolve
from boards.views import home, board_topics
from boards.models import Board


class HomeTests(TestCase):
    def setUp(self) -> None:
        self.board = Board.objects.create(
            name="Heheszki", description="All the heheszki."
        )
        url = reverse("home")
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        self.assertEqual(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse("board_topics", kwargs={"board_pk": self.board.pk})
        self.assertContains(self.response, f'href="{board_topics_url}"')


class BoardTopicsTests(TestCase):
    def setUp(self) -> None:
        Board.objects.create(name="Heheszki", description="All the heheszki.")

    def get_url(self, url: str):
        return self.client.get(url)

    def test_board_topics_view_success_status_code(self):
        url = reverse("board_topics", kwargs={"board_pk": 1})
        response = self.get_url(url)
        self.assertEqual(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse("board_topics", kwargs={"board_pk": 99})
        response = self.get_url(url)
        self.assertEqual(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve("/boards/1/")
        self.assertEqual(view.func, board_topics)

    def test_board_topics_view_contains_link_to_homepage(self):
        board_topics_url = reverse('board_topics', kwargs={'board_pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, f'href="{homepage_url}"')

