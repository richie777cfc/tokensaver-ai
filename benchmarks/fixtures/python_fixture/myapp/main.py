import os

from myapp.routes import router

DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = os.getenv("SECRET_KEY")


class App:
    pass


app = App()


@app.route("/")
def index():
    return {"name": "python-fixture"}


@app.get("/health")
def healthcheck():
    return {"ok": True, "db": bool(DATABASE_URL)}


def run():
    print("Running server")


def dev():
    print("Running dev server")
