import random
from typing import Optional

from .contexto import SesionSBC


MAX_HISTORIAL_FRASES = 5


def obtener_frase(
    sesion: SesionSBC,
    categoria: str,
    frases_disponibles: list[str],
) -> Optional[str]:
    if not frases_disponibles:
        return None
    candidatas = [
        f for f in frases_disponibles
        if f not in sesion.historial_frases_recientes
    ]
    if not candidatas:
        candidatas = frases_disponibles
        sesion.historial_frases_recientes.clear()
    elegida = random.choice(candidatas)
    sesion.historial_frases_recientes.append(elegida)
    if len(sesion.historial_frases_recientes) > MAX_HISTORIAL_FRASES:
        sesion.historial_frases_recientes.pop(0)
    return elegida


def construir_mensaje_inicial(
    nodo: dict,
    sesion: SesionSBC,
) -> str:
    mensajes = nodo.get("mensajes", {})
    intro = obtener_frase(sesion, "introduccion", mensajes.get("introduccion", []))
    pregunta = obtener_frase(sesion, "pregunta", mensajes.get("pregunta", []))
    partes = [p for p in [intro, pregunta] if p]
    return " ".join(partes) if partes else "¿En qué puedo ayudarte hoy?"


def construir_mensaje_confirmacion(
    nodo: dict,
    sesion: SesionSBC,
    opcion_texto: str,
) -> str:
    mensajes = nodo.get("mensajes", {})
    confirm = obtener_frase(
        sesion, "confirmacion", mensajes.get("confirmacion", [])
    )
    if confirm:
        return confirm
    return f"Gracias por tu respuesta. {'Entiendo.' if True else ''}"


def construir_mensaje_transicion(
    nodo_origen: dict,
    nodo_destino: dict,
    sesion: SesionSBC,
) -> str:
    mensajes = nodo_origen.get("mensajes", {})
    trans = obtener_frase(
        sesion, "transicion", mensajes.get("transicion", [])
    )
    return trans if trans else "Sigamos adelante."


def construir_mensaje_diagnostico(
    nodo: dict,
    sesion: SesionSBC,
) -> str:
    diagnostico = nodo.get("diagnostico", "")
    if not diagnostico:
        return ""
    partes = [f"**{diagnostico}**"]
    explicacion = nodo.get("recomendacion", "")
    if explicacion:
        partes.append(f"\n\n{explicacion}")
    return "".join(partes)
