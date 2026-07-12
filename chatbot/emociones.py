import re
from typing import Optional

EMOCIONES_PALABRAS: dict[str, list[str]] = {
    "enojo": [
        "enojo", "ira", "rabia", "frustrado", "frustracion", "molesto", "enojado",
        "furioso", "irritable", "irritado", "cabreado", "enfadado", "indignado",
        "resentido", "amargado", "hostil", "agresivo", "bronca", "coraje",
        "disgustado", "harto", "fastidiado", "impaciente", "exasperado",
    ],
    "tristeza": [
        "triste", "tristeza", "desanimo", "apatia", "melancolia", "deprimido",
        "bajo", "llorar", "llanto", "abatido", "desolado", "desconsolado",
        "desesperanza", "soledad", "solo", "vacío", "desmotivado", "desgana",
        "pesimista", "nostalgia", "pena", "sufrimiento", "desalentado",
        "descorazonado", "afligido", "decaído", "derrotado", "roto",
        "fatal", "pesimo", "horrible",
    ],
    "miedo": [
        "miedo", "ansiedad", "ansioso", "nervioso", "panico", "temeroso",
        "asustado", "preocupado", "angustiado", "angustia", "temor",
        "incertidumbre", "inseguro", "amenazado", "alarmado", "intranquilo",
        "desasosiego", "inquieto", "receloso", "desconfiado", "aterrado",
        "horrorizado", "espantado", "paralizado", "tenso", "tension",
        "taquicardia", "palpitaciones", "opresion", "ahogo",
    ],
    "alegria": [
        "alegre", "feliz", "contento", "bien", "genial", "excelente", "maravilloso",
        "fantastico", "optimista", "esperanzado", "motivado", "entusiasmado",
        "emocionado", "agradecido", "tranquilo", "calma", "paz", "sereno",
        "relajado", "energico", "vital", "positivo", "animado", "euforico",
    ],
    "vergüenza": [
        "vergüenza", "avergonzado", "humillado", "ridiculo", "pena ajena",
        "timidez", "timido", "cohibido", "intimidado", "expuesto",
    ],
    "asco": [
        "asco", "repulsion", "repugnancia", "desagrado", "disgusto",
        "nausea", "asqueado", "asqueroso", "horror", "aborrecimiento",
    ],
    "sorpresa": [
        "sorpresa", "sorprendido", "impactado", "asombrado", "incrédulo",
        "desconcertado", "confuso", "aturdido", "aturdido", "pasmar",
    ],
}

INTENSIDAD_ALTA: list[str] = [
    "muy", "mucho", "demasiado", "extremadamente", "terriblemente",
    "increiblemente", "sumamente", "absolutamente", "totalmente",
    "completamente", "profundamente", "intensamente", "enormemente",
    "excesivamente", "brutalmente", "altamente",
]

INTENSIDAD_BAJA: list[str] = [
    "un poco", "algo", "ligeramente", "levemente", "suavemente",
    "apenas", "poco", "poquito", "minimamente", "moderadamente",
]

EMOCION_A_RAMA: dict[str, list[str]] = {
    "enojo": ["N04", "N09"],
    "frustracion": ["N04", "N09"],
    "tristeza": ["N04", "N10"],
    "miedo": ["N02", "N05"],
    "ansiedad": ["N02", "N05"],
    "panico": ["N02", "N05"],
    "alegria": [],
    "vergüenza": ["N04"],
    "asco": ["N02"],
    "sorpresa": [],
}


def emocion_a_rama(emocion: str) -> list[str]:
    return EMOCION_A_RAMA.get(emocion, [])


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i")
    texto = texto.replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ñ", "n")
    texto = re.sub(r"[^a-z\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _normalizar_palabra(palabra: str) -> str:
    return _normalizar(palabra)


def detectar_emocion(texto: str) -> dict:
    normalizado = _normalizar(texto)
    puntajes: dict[str, float] = {}
    for emocion, palabras in EMOCIONES_PALABRAS.items():
        score = 0
        for palabra in palabras:
            palabra_norm = _normalizar_palabra(palabra)
            if palabra_norm in normalizado:
                score += 1
            elif any(palabra_norm in tok for tok in normalizado.split() if len(tok) >= 4):
                pass
        if score > 0:
            puntajes[emocion] = score

    principal = "neutral"
    max_score = 0
    if puntajes:
        principal = max(puntajes, key=puntajes.get)
        max_score = puntajes[principal]

    intensidad = _detectar_intensidad(normalizado, max_score)

    return {
        "principal": principal,
        "puntajes": puntajes,
        "intensidad": intensidad,
        "max_score": max_score,
    }


def _detectar_intensidad(normalizado: str, max_score: int) -> str:
    for mod in INTENSIDAD_ALTA:
        if mod in normalizado:
            return "alta"
    for mod in INTENSIDAD_BAJA:
        if mod in normalizado:
            return "baja"
    if max_score >= 2:
        return "alta"
    if max_score == 1:
        return "media"
    return "baja"


def emocion_a_rama(emocion: str) -> Optional[str]:
    return EMOCION_A_RAMA.get(emocion)
