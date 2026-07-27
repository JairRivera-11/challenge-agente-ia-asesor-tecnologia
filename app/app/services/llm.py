from functools import lru_cache

from google import genai
from google.genai import types

from app.config import get_settings
from app.prompts import SYSTEM_PROMPT, WEB_CONTEXT_TEMPLATE


class LLMError(Exception):
    pass


@lru_cache
def _default_client():
    settings = get_settings()
    if not settings.google_api_key:
        raise LLMError("Falta configurar GOOGLE_API_KEY")
    return genai.Client(api_key=settings.google_api_key)


def _get_client(api_key):
    if api_key:
        return genai.Client(api_key=api_key)
    return _default_client()


def _build_contents(history, message):
    contents = []
    for item in history:
        role = "model" if item["role"] == "assistant" else "user"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=item["content"])])
        )
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=message)])
    )
    return contents


def _build_system_prompt(web_context):
    if not web_context:
        return SYSTEM_PROMPT
    return SYSTEM_PROMPT + "\n\n" + WEB_CONTEXT_TEMPLATE.format(context=web_context)


def generate(message, history=None, web_context=None, api_key=None):
    settings = get_settings()
    client = _get_client(api_key)

    try:
        response = client.models.generate_content(
            model=settings.model_name,
            contents=_build_contents(history or [], message),
            config=types.GenerateContentConfig(
                system_instruction=_build_system_prompt(web_context),
                temperature=0.4,
            ),
        )
    except Exception as exc:
        raise LLMError("No se pudo generar la respuesta") from exc

    if not response.text:
        raise LLMError("El modelo devolvió una respuesta vacía")

    return response.text.strip()