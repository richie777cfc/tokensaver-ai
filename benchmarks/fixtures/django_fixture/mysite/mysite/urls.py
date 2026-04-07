"""URL configuration."""

from django.urls import path, include

urlpatterns = [
    path("api/blog/", include("blog.urls")),
    path("api/auth/login/", include("auth.urls")),
    path("admin/", include("django.contrib.admin.urls")),
]
