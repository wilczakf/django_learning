import django.db.models.base
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator

DELETED_USER = "non_existing_user"


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def board_posts(self):
        return Post.objects.filter(topic__board=self)

    def get_posts_count(self):
        return self.board_posts.count()

    def get_latest_post(self):
        return self.board_posts.order_by("-created_at").first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name="topics", on_delete=models.CASCADE)
    starting_user = models.ForeignKey(
        User, related_name="topics", on_delete=models.SET(value=DELETED_USER)
    )
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name="posts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(
        User, related_name="posts", on_delete=models.SET(value=DELETED_USER)
    )
    updated_by = models.ForeignKey(
        User, null=True, related_name="+", on_delete=models.SET(value=DELETED_USER)
    )

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)
