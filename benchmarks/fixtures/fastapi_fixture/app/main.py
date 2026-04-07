"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Demo API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"])

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/users")
async def list_users():
    return []


@app.post("/api/users")
async def create_user():
    return {"id": 1}


@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id}


@app.put("/api/users/{user_id}")
async def update_user(user_id: int):
    return {"id": user_id}


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    return {"deleted": True}
