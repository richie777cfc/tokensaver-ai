"""Blog URL patterns."""

from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list, name="post-list"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
    path("posts/<int:pk>/comments/", views.comment_list, name="comment-list"),
]
