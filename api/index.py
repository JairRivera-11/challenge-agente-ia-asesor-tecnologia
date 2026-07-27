from fastapi import FastAPI

from app.config import get_settings

app = FastAPI(title="Asistente Electronicos.com")


@app.get("/api/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.model_name,
        "google_key_loaded": bool(settings.google_api_key),
        "tavily_key_loaded": bool(settings.tavily_api_key),
    }