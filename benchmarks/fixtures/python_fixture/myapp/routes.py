import os


class Router:
    pass


router = Router()

API_TOKEN = os.getenv("API_TOKEN")


@router.get("/api/users")
def list_users():
    return {"users": []}


@router.post("/api/users")
def create_user():
    return {"created": True}


@router.get("/api/users/{user_id}")
def get_user(user_id: str):
    return {"id": user_id}


@router.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    return {"deleted": True}
