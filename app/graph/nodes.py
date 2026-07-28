from app.services.llm import clasificar, generar
from app.services.search import SearchError, buscar


def clasificar_consulta(estado):
    salida = clasificar(estado["mensaje"], api_key=estado.get("google_api_key"))
    linea = salida.strip().split("\n")[0]
    sin_busqueda = {"necesita_busqueda": False, "consulta_busqueda": ""}

    if "|" not in linea:
        return sin_busqueda

    encabezado, consulta = linea.split("|", 1)

    if encabezado.strip().upper() not in ("SI", "SÍ"):
        return sin_busqueda

    return {"necesita_busqueda": True, "consulta_busqueda": consulta.strip()}


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
