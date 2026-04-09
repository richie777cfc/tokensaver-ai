from fastapi import FastAPI
import os

app = FastAPI()
API_KEY = os.getenv("BACKEND_API_KEY")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
