const URL_CHAT = "/api/chat";

const historial = [];

const mensajes = document.getElementById("mensajes");
const formulario = document.getElementById("formulario");
const campoTexto = document.getElementById("campo-texto");
const botonEnviar = document.getElementById("boton-enviar");
const botonPanel = document.getElementById("boton-panel");

let esperando = false;
let filaEscribiendo = null;

function bajarAlFinal() {
  mensajes.scrollTop = mensajes.scrollHeight;
}

function crearBurbuja(texto, tipo) {
  const fila = document.createElement("div");
  fila.className = tipo === "usuario" ? "fila fila-usuario" : "fila fila-asistente";

  const burbuja = document.createElement("div");
  burbuja.className = "burbuja burbuja-" + tipo;
  burbuja.textContent = texto;

  fila.appendChild(burbuja);
  mensajes.appendChild(fila);
  bajarAlFinal();

  return burbuja;
}

function marcarBusquedaWeb(burbuja) {
  const marca = document.createElement("span");
  marca.className = "marca-web";
  marca.textContent = "Información verificada con búsqueda web";
  burbuja.appendChild(marca);
  bajarAlFinal();
}

function mostrarEscribiendo() {
  const fila = document.createElement("div");
  fila.className = "fila fila-asistente";

  const burbuja = document.createElement("div");
  burbuja.className = "burbuja burbuja-asistente escribiendo";

  for (let i = 0; i < 3; i++) {
    const punto = document.createElement("span");
    punto.className = "punto";
    burbuja.appendChild(punto);
  }

  fila.appendChild(burbuja);
  mensajes.appendChild(fila);
  bajarAlFinal();

  filaEscribiendo = fila;
}

function quitarEscribiendo() {
  if (filaEscribiendo) {
    filaEscribiendo.remove();
    filaEscribiendo = null;
  }
}

function bloquear(valor) {
  esperando = valor;
  campoTexto.disabled = valor;
  botonEnviar.disabled = valor;
}

function ajustarAltura() {
  campoTexto.style.height = "auto";
  campoTexto.style.height = campoTexto.scrollHeight + "px";
}

function obtenerClavesUsuario() {
  return {};
}

function armarCabeceras() {
  const cabeceras = { "Content-Type": "application/json" };
  const claves = obtenerClavesUsuario();

  if (claves.google) {
    cabeceras["X-Google-Key"] = claves.google;
  }
  if (claves.tavily) {
    cabeceras["X-Tavily-Key"] = claves.tavily;
  }

  return cabeceras;
}

function textoDeError(codigo) {
  if (codigo === 422) {
    return "No pude leer ese mensaje. Revisa que no esté vacío y que no sea demasiado largo.";
  }
  if (codigo === 502) {
    return "Tuve un problema al generar la respuesta. Vuelve a intentarlo.";
  }
  if (codigo === 503) {
    return "El asistente no está configurado en este momento. Intentar de nuevo no va a ayudar, avisa al equipo de Electronicos.com.";
  }
  return "Ocurrió un error inesperado. Vuelve a intentarlo en un momento.";
}

async function pedirRespuesta(mensaje) {
  const peticion = await fetch(URL_CHAT, {
    method: "POST",
    headers: armarCabeceras(),
    body: JSON.stringify({ mensaje: mensaje, historial: historial }),
  });

  if (!peticion.ok) {
    return { error: textoDeError(peticion.status) };
  }

  return await peticion.json();
}

async function enviarMensaje(mensaje) {
  crearBurbuja(mensaje, "usuario");
  bloquear(true);
  mostrarEscribiendo();

  let datos;

  try {
    datos = await pedirRespuesta(mensaje);
  } catch (error) {
    datos = { error: "No hay conexión con el servidor. Revisa tu internet y vuelve a intentarlo." };
  }

  quitarEscribiendo();

  if (datos.error) {
    crearBurbuja(datos.error, "error");
  } else {
    const burbuja = crearBurbuja(datos.respuesta, "asistente");

    if (datos.busco_en_web) {
      marcarBusquedaWeb(burbuja);
    }

    historial.push({ role: "user", content: mensaje });
    historial.push({ role: "assistant", content: datos.respuesta });
  }

  bloquear(false);
  campoTexto.focus();
}

formulario.addEventListener("submit", function (evento) {
  evento.preventDefault();

  if (esperando) {
    return;
  }

  const mensaje = campoTexto.value.trim();

  if (!mensaje) {
    return;
  }

  campoTexto.value = "";
  ajustarAltura();
  enviarMensaje(mensaje);
});

campoTexto.addEventListener("keydown", function (evento) {
  if (evento.key === "Enter" && !evento.shiftKey) {
    evento.preventDefault();
    formulario.requestSubmit();
  }
});

campoTexto.addEventListener("input", ajustarAltura);

botonPanel.addEventListener("click", function () {
  const visible = document.body.classList.toggle("con-panel");
  botonPanel.textContent = visible ? "Ver chat" : "Ver flujo";
  botonPanel.setAttribute("aria-expanded", visible);
});

campoTexto.focus();
