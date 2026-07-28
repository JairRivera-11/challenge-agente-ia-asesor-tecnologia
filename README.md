# Asistente de Electronicos.com

Chatbot que asesora a clientes sobre productos tecnológicos. Hace preguntas antes
de recomendar, explica los tecnicismos en lenguaje simple y busca en la web cuando
la consulta depende de datos que cambian, como precios o disponibilidad.

## Stack

- **FastAPI** como único entrypoint, pensado para correr como función serverless
- **LangGraph** para el flujo de decisión del agente
- **google-genai** (Gemini) para clasificar y redactar
- **Tavily** para la búsqueda web
- Front en HTML, CSS y JavaScript a mano, sin frameworks ni librerías

## Cómo funciona

Cada mensaje pasa por un grafo de tres nodos:

```
mensaje -> clasificar -> responder -> respuesta
                |            ^
                v            |
             buscar ---------+
```

**clasificar** decide si la consulta necesita información actualizada. Si la
respuesta se puede dar con conocimiento general —qué es una pantalla OLED, qué
laptop conviene para programar— pasa directo a redactar. Si depende de precios,
stock o modelos recientes, además arma la consulta de búsqueda con marca y modelo
explícitos, en lugar de reusar el texto crudo del usuario.

**buscar** consulta Tavily y recorta las fuentes más relevantes. Se devuelven los
resultados formateados como texto y no el resumen automático del buscador, para
que la redacción quede siempre del lado del prompt del asistente.

**responder** arma la respuesta con el historial de la conversación y, si hubo
búsqueda, con el contexto web como fuente principal.

Si la búsqueda falla, el asistente responde igual sin contexto web. El prompt le
prohíbe inventar precios y especificaciones, así que en ese caso avisa que no
pudo confirmar el dato en lugar de cortar la conversación.

## Correr en local

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env      # completar las dos API keys
.venv/bin/python -m uvicorn api.index:app --reload
```

Queda en http://127.0.0.1:8000.

Las keys se sacan de [Google AI Studio](https://aistudio.google.com/apikey) y de
[Tavily](https://app.tavily.com).

## Variables de entorno

| Variable | Para qué sirve |
|---|---|
| `GOOGLE_API_KEY` | Key de Gemini. Sin esto el asistente responde 503 |
| `TAVILY_API_KEY` | Key de Tavily. Sin esto no hay búsqueda web, pero el chat sigue andando |
| `MODEL_NAME` | Modelo que redacta las respuestas |
| `ROUTER_MODEL_NAME` | Modelo que clasifica. Va separado para no gastar dos veces la misma cuota diaria |
| `ALLOW_USER_KEYS` | Si es `false`, se ignoran las keys que mande el usuario desde el navegador |

## API

### `POST /api/chat`

```json
{
  "mensaje": "¿Cuánto cuesta el iPhone 17 en México?",
  "historial": [{ "role": "user", "content": "hola" }]
}
```

Respuesta:

```json
{
  "respuesta": "...",
  "busco_en_web": true
}
```

Headers opcionales: `X-Google-Key` y `X-Tavily-Key`.

| Código | Significado |
|---|---|
| `422` | El mensaje no pasó la validación |
| `502` | Falló la generación. Se puede reintentar |
| `503` | No hay ninguna key de Gemini configurada. Reintentar no sirve |

### `GET /api/health`

Devuelve el modelo en uso y si las keys del servidor están cargadas. Nunca
devuelve el valor de las keys.

## API keys del usuario

El panel lateral permite cargar keys propias. Viajan por header, se usan
únicamente en esa request y se descartan: no se guardan en el servidor ni en el
navegador. Al recargar la página se pierden.

Las keys del servidor viven en variables de entorno y no se devuelven por la API
ni se escriben en los logs.

## Deploy en Vercel

El `vercel.json` rutea todo el tráfico a `api/index.py` e incluye `app/` y
`public/` en el bundle de la función.

Antes de desplegar hay que cargar las variables de entorno en el panel del
proyecto. El `.env` no se sube al repo.

## Estructura

```
api/index.py            FastAPI, endpoints y archivos estáticos
app/config.py           settings desde variables de entorno
app/prompts.py          prompt del asistente, del contexto web y del router
app/services/llm.py     Gemini: clasificar y generar
app/services/search.py  Tavily
app/graph/              estado, nodos y armado del grafo
public/                 front del chat
```

## Límites conocidos

El free tier de Gemini permite 20 requests por día y por modelo. Cada mensaje
consume uno del modelo de respuesta y uno del router, así que alcanza para unos
20 mensajes diarios. Al agotarse, la API devuelve 502. Para uso sostenido hay que
habilitar facturación en el proyecto de Google Cloud.
