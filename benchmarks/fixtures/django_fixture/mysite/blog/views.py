"""Blog views."""

import os

from django.http import JsonResponse

CACHE_TTL = os.environ["CACHE_TTL"]


def post_list(request):
    return JsonResponse({"posts": []})


def post_detail(request, pk):
    return JsonResponse({"id": pk})


def comment_list(request, pk):
    return JsonResponse({"comments": []})
