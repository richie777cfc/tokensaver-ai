"""Pydantic and SQLModel models."""

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str


class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
