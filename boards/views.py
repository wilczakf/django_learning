from django.shortcuts import render, get_object_or_404
from boards.models import Board


def home(request):
    boards = Board.objects.all()
    return render(request, "home.html", {"boards": boards})


def board_topics(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    return render(request, "topics.html", {"board": board})


def new_topic(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    return render(request, "new_topic.html", {"board": board})

