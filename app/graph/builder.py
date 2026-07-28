from langgraph.graph import END, START, StateGraph

from app.graph.nodes import buscar_en_web, clasificar_consulta, decidir_camino, responder
from app.graph.state import EstadoChat


def armar_grafo():
    constructor = StateGraph(EstadoChat)

    constructor.add_node("clasificar", clasificar_consulta)
    constructor.add_node("buscar", buscar_en_web)
    constructor.add_node("responder", responder)

    constructor.add_edge(START, "clasificar")
    constructor.add_conditional_edges(
        "clasificar",
        decidir_camino,
        {"buscar": "buscar", "responder": "responder"},
    )
    constructor.add_edge("buscar", "responder")
    constructor.add_edge("responder", END)

    return constructor.compile()


grafo = armar_grafo()
