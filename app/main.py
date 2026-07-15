from fastapi import FastAPI
from app.config import Settings

settings = Settings()

app = FastAPI(
    title=settings.APP_NAME,
    open_api_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/")
def read_root():
    return { "hello": "It is I!" }

@app.get(settings.APP_STATUS)
def app_status():
    return { "status": "OK" }
