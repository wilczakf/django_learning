from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from accounts import views as accounts_views
from boards import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", accounts_views.signup, name="signup"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password/password_reset.html",
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("settings/password/", auth_views.PasswordChangeView.as_view(template_name="password/password_change.html"), name="password_change"),
    path("settings/password/done/", auth_views.PasswordChangeDoneView.as_view(template_name="password/password_change_done.html"), name="password_change_done"),
    re_path(r"^boards/(?P<board_pk>\d+)/$", views.board_topics, name="board_topics"),
    re_path(r"^boards/(?P<board_pk>\d+)/new/$", views.new_topic, name="new_topic"),
    re_path(r"^boards/(?P<board_pk>\d+)/topics/(?P<topic_pk>\d+)/$", views.topic_posts, name="topic_posts"),
    re_path(r"^boards/(?P<board_pk>\d+)/topics/(?P<topic_pk>\d+)/reply/$", views.reply_topic, name="reply_topic"),
    path("admin/", admin.site.urls),
]

# todo list
#  - add sites about author (additional view and template in html)
