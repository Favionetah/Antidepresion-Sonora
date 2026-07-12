import random
from typing import Optional

from .contexto import SesionSBC


MAX_HISTORIAL_FRASES = 5

FRASES_EMPATICAS: dict[str, list[str]] = {
    "enojo": [
        "Parece que hay frustración o enojo acumulado. Es válido sentirlo.",
        "Se nota que algo te tiene molesto. Cuéntame más.",
        "La energía del enojo también puede canalizarse de forma positiva.",
    ],
    "tristeza": [
        "Veo que estás pasando por un momento difícil. Estoy aquí para acompañarte.",
        "La tristeza también necesita ser escuchada. Cuéntame cómo te sientes.",
        "A veces las palabras no alcanzan, pero puedes intentarlo.",
    ],
    "miedo": [
        "Parece que hay ansiedad o preocupación en lo que dices. Respira profundo.",
        "Entiendo que esto puede ser abrumador. Tómate tu tiempo.",
        "Estás en un espacio seguro. Aquí no hay prisas.",
    ],
    "alegria": [
        "Qué bueno que te sientes bien. Eso es importante.",
        "Me alegra escuchar eso. Sigamos explorando.",
    ],
    "neutral": [
        "Cuéntame un poco más para entenderte mejor.",
        "Gracias por compartir. Dime más sobre cómo te sientes.",
    ],
}

FRASES_CLARIFICACION_EMPATICA: dict[str, list[str]] = {
    "enojo": [
        "Dijiste algo que suena a frustración. ¿Eso se manifiesta más en tu cuerpo o en tus pensamientos?",
        "Esa molestia que sientes, ¿es algo físico o más bien emocional?",
    ],
    "tristeza": [
        "Esa tristeza que mencionas, ¿la sientes más en el cuerpo o en la mente?",
        "La melancolía puede sentirse como un peso físico o como niebla mental. ¿Cuál es tu caso?",
    ],
    "miedo": [
        "Esa ansiedad que sientes, ¿se manifiesta más con síntomas físicos o con pensamientos acelerados?",
        "El miedo puede sentirse en el cuerpo (palpitaciones, opresión) o en la mente (no dejar de pensar). ¿Qué predomina?",
    ],
}

FRASES_FEEDBACK: list[str] = [
    "¿Cómo te hizo sentir esta música? ¿Resuena con lo que necesitabas?",
    "¿Sientes que esta playlist se alinea con tu estado de ánimo actual?",
    "Me encantaría saber qué tal te pareció la recomendación. ¿Te gustó?",
    "¿Esta música te ayudó a conectar con lo que sientes?",
]


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


def construir_mensaje_empatico(sesion: SesionSBC) -> Optional[str]:
    emotion = sesion.emotion_principal
    intensidad = sesion.intensidad_emocional
    frases = FRASES_EMPATICAS.get(emotion)
    if not frases:
        return None
    return obtener_frase(sesion, f"empatico_{emotion}", frases)


def construir_clarificacion_empatica(sesion: SesionSBC, opciones: list[dict]) -> Optional[str]:
    emotion = sesion.emotion_principal
    if emotion == "neutral" or emotion not in FRASES_CLARIFICACION_EMPATICA:
        return None
    frases = FRASES_CLARIFICACION_EMPATICA[emotion]
    return random.choice(frases) if frases else None


def construir_mensaje_feedback() -> str:
    return random.choice(FRASES_FEEDBACK)


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
    return "Gracias por tu respuesta."


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
