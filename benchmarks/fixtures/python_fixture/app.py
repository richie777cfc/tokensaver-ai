import os

from myapp.main import app

API_KEY = os.getenv("SERVICE_API_KEY")


@app.get("/status")
def status():
    return {"ok": True, "api_key_present": bool(API_KEY)}
