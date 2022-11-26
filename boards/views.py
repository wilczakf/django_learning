from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from boards.models import Board, Topic, Post


def home(request):
    boards = Board.objects.all()
    return render(request, "home.html", {"boards": boards})


def board_topics(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    return render(request, "topics.html", {"board": board})


def new_topic(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)

    if request.method == "POST":
        subject = request.POST["subject"]
        message = request.POST["message"]

        user = User.objects.first()  # todo - get currently logged user

        topic = Topic.objects.create(subject=subject, board=board, starting_user=user)

        post = Post.objects.create(message=message, topic=topic, created_by=user)

        return redirect(
            "board_topics", board_pk=board.pk
        )  # todo redirect to created topic page

    return render(request, "new_topic.html", {"board": board})
