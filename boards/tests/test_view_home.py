from django.test import TestCase
from django.urls import reverse, resolve
from boards.views import BoardListView
from boards.models import Board


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
        self.assertEqual(view.func.view_class, BoardListView)

    def test__home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse("board_topics", kwargs={"board_pk": self.board.pk})
        self.assertContains(self.response, f'href="{board_topics_url}"')
