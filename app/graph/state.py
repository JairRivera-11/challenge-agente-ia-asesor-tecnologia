from typing import List, TypedDict


class EstadoChat(TypedDict, total=False):
    mensaje: str
    historial: List[dict]
    google_api_key: str
    tavily_api_key: str
    necesita_busqueda: bool
    consulta_busqueda: str
    contexto_web: str
    busco_en_web: bool
    respuesta: str
