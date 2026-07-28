from functools import lru_cache

from tavily import TavilyClient

from app.config import get_settings


class SearchError(Exception):
    pass


MAX_RESULTADOS = 3
MAX_CHARS_POR_RESULTADO = 800


@lru_cache
def _cliente_por_defecto():
    settings = get_settings()
    if not settings.tavily_api_key:
        raise SearchError("Falta configurar TAVILY_API_KEY")
    return TavilyClient(api_key=settings.tavily_api_key)


def _obtener_cliente(api_key):
    if api_key:
        return TavilyClient(api_key=api_key)
    return _cliente_por_defecto()


def _formatear(resultados):
    bloques = []
    for item in resultados:
        contenido = (item.get("content") or "").strip()
        if not contenido:
            continue
        bloques.append(
            f"Fuente: {item.get('title', 'sin titulo')}\n"
            f"URL: {item.get('url', '')}\n"
            f"{contenido[:MAX_CHARS_POR_RESULTADO]}"
        )
    return "\n\n---\n\n".join(bloques)


def buscar(query, api_key=None):
    client = _obtener_cliente(api_key)

    try:
        response = client.search(
            query=query,
            max_results=MAX_RESULTADOS,
            search_depth="basic",
        )
    except Exception as exc:
        raise SearchError("La busqueda web fallo") from exc

    return _formatear(response.get("results", []))