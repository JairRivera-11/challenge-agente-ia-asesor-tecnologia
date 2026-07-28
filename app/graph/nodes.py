from app.services.llm import clasificar, generar
from app.services.search import SearchError, buscar


def _leer_decision(salida):
    linea = (salida or "").strip().splitlines()[0] if salida else ""
    partes = linea.split("|", 1)
    encabezado = partes[0].strip().upper()

    if encabezado not in ("SI", "SÍ") or len(partes) < 2:
        return False, ""

    return True, partes[1].strip()


def clasificar_consulta(estado):
    salida = clasificar(estado["mensaje"], api_key=estado.get("google_api_key"))
    necesita, consulta = _leer_decision(salida)

    return {"necesita_busqueda": necesita, "consulta_busqueda": consulta}


def decidir_camino(estado):
    if estado.get("necesita_busqueda") and estado.get("consulta_busqueda"):
        return "buscar"
    return "responder"


def buscar_en_web(estado):
    try:
        contexto = buscar(estado["consulta_busqueda"], api_key=estado.get("tavily_api_key"))
    except SearchError:
        return {"contexto_web": "", "busco_en_web": False}

    return {"contexto_web": contexto, "busco_en_web": bool(contexto)}


def responder(estado):
    texto = generar(
        estado["mensaje"],
        historial=estado.get("historial"),
        contexto_web=estado.get("contexto_web"),
        api_key=estado.get("google_api_key"),
    )

    return {"respuesta": texto}
