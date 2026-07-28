from pathlib import Path
from typing import List, Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.builder import grafo
from app.services.llm import LLMError
from app.services.search import SearchError

RAIZ = Path(__file__).resolve().parent.parent

app = FastAPI(title="Asistente Electronicos.com")


class MensajeHistorial(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class PeticionChat(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)
    historial: List[MensajeHistorial] = Field(default_factory=list, max_length=40)


def _clave_permitida(clave):
    if not clave:
        return None
    if not get_settings().allow_user_keys:
        return None
    return clave.strip()


@app.get("/api/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.model_name,
        "google_key_loaded": bool(settings.google_api_key),
        "tavily_key_loaded": bool(settings.tavily_api_key),
    }


@app.post("/api/chat")
def chat(peticion: PeticionChat, x_google_key=Header(None), x_tavily_key=Header(None)):
    settings = get_settings()
    google_key = _clave_permitida(x_google_key)
    tavily_key = _clave_permitida(x_tavily_key)

    if not settings.google_api_key and not google_key:
        raise HTTPException(status_code=503, detail="El asistente no está configurado")

    estado = {
        "mensaje": peticion.mensaje,
        "historial": [item.model_dump() for item in peticion.historial],
        "google_api_key": google_key,
        "tavily_api_key": tavily_key,
    }

    try:
        resultado = grafo.invoke(estado)
    except (LLMError, SearchError) as exc:
        raise HTTPException(status_code=502, detail="No se pudo generar la respuesta") from exc

    return {
        "respuesta": resultado["respuesta"],
        "busco_en_web": bool(resultado.get("busco_en_web")),
    }


app.mount("/", StaticFiles(directory=RAIZ / "public", html=True), name="public")
