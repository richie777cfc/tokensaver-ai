import os


class App:
    pass


app = App()
API_KEY = os.getenv("SERVICE_API_KEY")


@app.get("/health")
def healthcheck():
    return {"ok": True, "api_key_present": bool(API_KEY)}
