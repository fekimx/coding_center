
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("post/", views.post, name="post"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("update/<int:post_id>", views.update_post, name="update"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("following/", views.following, name="following"),
    path("like/<int:post_id>", views.like, name="like"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
