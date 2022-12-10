from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from boards.forms import NewTopicForm, PostForm
from boards.models import Board, Topic, Post


class BoardListView(ListView):
    model = Board
    context_object_name = "boards"
    template_name = "home.html"


class TopicListView(ListView):
    model = Topic
    context_object_name = "topics"
    template_name = "topics.html"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs["board"] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get("board_pk"))
        queryset = self.board.topics.order_by("-last_updated").annotate(
            replies=Count("posts") - 1
        )
        return queryset


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "topic_posts.html"
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs["topic"] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(
            Topic, board__pk=self.kwargs.get("board_pk"), pk=self.kwargs.get("topic_pk")
        )
        queryset = self.topic.posts.order_by("-created_at")
        return queryset


@login_required
def new_topic(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)

    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starting_user = request.user
            topic.save()

            Post.objects.create(
                message=form.cleaned_data.get("message"),
                topic=topic,
                created_by=request.user,
            )

            return redirect("topic_posts", board_pk=board_pk, topic_pk=topic.pk)

    else:
        form = NewTopicForm()

    return render(request, "new_topic.html", {"board": board, "form": form})


@login_required
def reply_topic(request, board_pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=board_pk, pk=topic_pk)
    if request.method == "POST":  # todo why GET instead of POST is working ??
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect("topic_posts", board_pk=board_pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, "reply_topic.html", {"topic": topic, "form": form})


@method_decorator(login_required, name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    fields = ("message",)
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()

        return redirect(
            "topic_posts", board_pk=post.topic.board.pk, topic_pk=post.topic.pk
        )
