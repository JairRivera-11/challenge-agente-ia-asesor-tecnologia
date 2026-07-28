from functools import lru_cache

from google import genai
from google.genai import types

from app.config import get_settings
from app.prompts import ROUTER_PROMPT, SYSTEM_PROMPT, WEB_CONTEXT_TEMPLATE


class LLMError(Exception):
    pass


@lru_cache
def _cliente_por_defecto():
    settings = get_settings()
    if not settings.google_api_key:
        raise LLMError("Falta configurar GOOGLE_API_KEY")
    return genai.Client(api_key=settings.google_api_key)


def _obtener_cliente(api_key):
    if api_key:
        return genai.Client(api_key=api_key)
    return _cliente_por_defecto()


def _armar_contenidos(historial, mensaje):
    contenidos = []
    for item in historial:
        role = "model" if item["role"] == "assistant" else "user"
        contenidos.append(
            types.Content(role=role, parts=[types.Part.from_text(text=item["content"])])
        )
    contenidos.append(
        types.Content(role="user", parts=[types.Part.from_text(text=mensaje)])
    )
    return contenidos


def _armar_prompt_sistema(contexto_web):
    if not contexto_web:
        return SYSTEM_PROMPT
    return SYSTEM_PROMPT + "\n\n" + WEB_CONTEXT_TEMPLATE.format(context=contexto_web)


def _pedir_al_modelo(api_key, contenidos, prompt_sistema, temperatura, modelo):
    client = _obtener_cliente(api_key)

    try:
        respuesta = client.models.generate_content(
            model=modelo,
            contents=contenidos,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                temperature=temperatura,
            ),
        )
    except Exception as exc:
        raise LLMError("No se pudo generar la respuesta") from exc

    if not respuesta.text:
        raise LLMError("El modelo devolvió una respuesta vacía")

    return respuesta.text.strip()


def generar(mensaje, historial=None, contexto_web=None, api_key=None):
    settings = get_settings()
    contenidos = _armar_contenidos(historial or [], mensaje)
    prompt_sistema = _armar_prompt_sistema(contexto_web)
    return _pedir_al_modelo(api_key, contenidos, prompt_sistema, 0.4, settings.model_name)


def clasificar(mensaje, api_key=None):
    settings = get_settings()
    contenidos = _armar_contenidos([], mensaje)
    return _pedir_al_modelo(api_key, contenidos, ROUTER_PROMPT, 0, settings.router_model_name)
