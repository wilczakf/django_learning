from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from boards.models import Board, Post, Topic
from boards.views import PostListView


class TopicPostsTests(TestCase):
    def setUp(self) -> None:
        board = Board.objects.create(name="board", description="About board.")
        user = User.objects.create_user(
            username="test_user", email="user@test.com", password="test_password"
        )
        topic = Topic.objects.create(
            subject="Test topic.", board=board, starting_user=user
        )

        Post.objects.create(message="Test message", topic=topic, created_by=user)
        url = reverse(
            "topic_posts", kwargs={"board_pk": board.pk, "topic_pk": topic.pk}
        )
        self.response = self.client.get(url)

    def test__status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test__view_function(self):
        view = resolve("/boards/1/topics/1/")
        self.assertEqual(view.func.view_class, PostListView)
