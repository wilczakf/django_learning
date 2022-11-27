from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from boards.forms import NewTopicForm
from boards.models import Board, Topic, Post


def home(request):
    boards = Board.objects.all()
    return render(request, "home.html", {"boards": boards})


def board_topics(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    return render(request, "topics.html", {"board": board})


def new_topic(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    user = User.objects.first()  # todo get currently logged user

    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starting_user = user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get("message"),
                topic=topic,
                created_by=user
            )

            return redirect(
                "board_topics", board_pk=board.pk
            )  # todo redirect to created topic page

    else:
        form = NewTopicForm()

    return render(request, "new_topic.html", {"board": board, "form": form})
