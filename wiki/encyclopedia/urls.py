from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry, name="entry"),
    path("query/", views.query, name="query"),
    path("create_page/", views.create_page, name="create_page"),
    path("create/", views.create, name="create"),
    path("random/", views.random_page, name="random"),
    path("edit/", views.edit, name="edit"),
    path("save/", views.save, name="save")
]
