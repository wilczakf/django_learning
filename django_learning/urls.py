from django.contrib import admin
from django.urls import path, re_path
from accounts import views as accounts_views
from boards import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", accounts_views.signup, name="signup"),
    re_path(r"^boards/(?P<board_pk>\d+)/$", views.board_topics, name="board_topics"),
    re_path(r"^boards/(?P<board_pk>\d+)/new/$", views.new_topic, name="new_topic"),
    path("admin/", admin.site.urls),
]

# todo list
#  - add sites about author (additional view and template in html)
