"""Additional API routes."""

import os

from fastapi import APIRouter

router = APIRouter()

API_KEY = os.getenv("API_KEY")
REDIS_URL = os.getenv("REDIS_URL")


@router.get("/api/posts")
async def list_posts():
    return []


@router.post("/api/posts")
async def create_post():
    return {"id": 1}


@router.get("/api/posts/{post_id}")
async def get_post(post_id: int):
    return {"id": post_id}


@router.delete("/api/posts/{post_id}")
async def delete_post(post_id: int):
    return {"deleted": True}
