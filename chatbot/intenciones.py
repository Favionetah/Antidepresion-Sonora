import re
from typing import Optional

SINONIMOS: dict[str, list[str]] = {
    "fisico": ["corporal", "muscular", "organico", "somatico", "cuerpo", "fisicamente",
               "taquicardia", "palpitaciones", "opresion", "pecho", "tension", "insomnio", "dolor"],
    "fisic": ["fisico", "corporal", "muscular", "organico", "somatico", "cuerpo",
              "taquicardia", "palpitaciones", "opresion", "pecho", "tension", "insomnio", "dolor"],
    "tension": ["tenso", "tensa", "tirante", "contracto", "rigido", "estresado"],
    "insomnio": ["dormir", "sueno", "desvelo", "insomne", "descansar", "dormido"],
    "dolor": ["duele", "dolorido", "molestia", "padecimiento", "dolores", "adolorido"],
    "taquicardia": ["palpitaciones", "ritmo", "latiendo", "cardiaco", "corazon"],
    "opresion": ["pecho", "oprimido", "apretado", "presion", "ahogo", "respirar"],
    "panico": ["crisis", "ataque", "miedo", "angustia", "desesperacion", "nervios"],
    "mental": ["cognitivo", "pensamiento", "mente", "cabeza", "intelectual", "razonar"],
    "bloqueo": ["bloqueado", "trabado", "estancado", "en blanco", "vacio", "nublado"],
    "concentracion": ["concentrar", "enfocar", "atencion", "distraer", "foco", "disperso"],
    "overthinking": ["acelerado", "vuelta", "rumiar", "insistir", "repetitivo"],
    "emocional": ["sentimiento", "animo", "afectivo", "sentir"],
    "irritabilidad": ["irritable", "enojo", "ira", "frustrado", "molesto", "enojado", "rabia"],
    "tristeza": ["triste", "desanimo", "apatia", "melancolia", "deprimido", "bajo", "llorar"],
    "agudo": ["repentino", "intenso", "fuerte", "grave", "urgente"],
    "cronico": ["constante", "persistente", "continuo", "permanente", "diario", "siempre"],
    "cansancio": ["fatiga", "agotado", "pesado", "debilitado", "somnoliento"],
    "calma": ["relajar", "relajacion", "tranquilo", "paz", "sereno", "bajar"],
    "energia": ["liberar", "descargar", "canalizar", "soltar", "expresar", "sacar"],
    "foco": ["enfoque", "concentrar", "estudio", "trabajo", "productividad", "atento"],
    "sueno": ["dormir", "descanso", "profundo", "delta", "adormecer"],
}

STEMMAP: dict[str, str] = {
    "tenso": "tension",
    "tensa": "tension",
    "duele": "dolor",
    "duelen": "dolor",
    "dormir": "insomnio",
    "desvelo": "insomnio",
    "enojado": "irritabilidad",
    "molesto": "irritabilidad",
    "frustrado": "irritabilidad",
    "cansado": "cansancio",
    "agotado": "cansancio",
    "relajar": "calma",
    "relajado": "calma",
    "concentrar": "concentracion",
    "enfocar": "foco",
    "triste": "tristeza",
    "deprimido": "tristeza",
    "acelerado": "overthinking",
    "mente": "mental",
    "cabeza": "mental",
    "blanco": "bloqueo",
    "nublado": "bloqueo",
    "pensar": "mental",
    "sentir": "emocional",
    "cuerpo": "fisico",
    "nervioso": "panico",
}

STOPWORDS = {
    "un", "una", "unas", "unos", "el", "la", "los", "las", "lo",
    "me", "te", "se", "nos", "le", "les",
    "que", "como", "cual", "cuales", "quien", "quienes",
    "mi", "tu", "su", "mis", "tus", "sus",
    "y", "e", "o", "u", "a", "ante", "bajo", "con", "contra",
    "de", "desde", "en", "entre", "hacia", "hasta", "para", "por",
    "segun", "sin", "sobre", "tras", "del",
    "este", "esta", "estos", "estas", "esto",
    "ese", "esa", "esos", "esas", "eso",
    "aquel", "aquella", "aquellos", "aquellas", "aquello",
    "no", "si", "ya", "tambien", "pero", "mas", "menos",
    "muy", "mucho", "poco", "bastante", "demasiado",
    "bien", "mal", "asi", "solo", "solamente",
    "cuando", "donde", "porque", "entonces", "pues",
    "es", "son", "fue", "era", "ser", "estar", "estoy", "esta",
    "he", "has", "ha", "han", "hemos", "haber",
    "hay", "habia", "hubo", "tener", "tengo", "tiene", "tienen",
    "hacer", "hago", "hace", "hacen",
    "poder", "puedo", "puede", "pueden",
    "querer", "quiero", "quiere", "quieren",
    "decir", "digo", "dice", "dicen",
    "saber", "se", "sabe", "saben",
    "creo", "crees", "cree", "creen",
    "sentir", "siento", "siente", "sienten",
    "necesitar", "necesito", "necesita", "necesitan",
    "todo", "toda", "todos", "todas",
    "cada", "algun", "alguna", "algunos", "algunas",
    "ningun", "ninguna", "ningunos", "ningunas",
    "otro", "otra", "otros", "otras",
    "mismo", "misma", "mismos", "mismas",
    "tan", "tanto", "tanta", "tantos", "tantas",
    "aqui", "alli", "alla", "acá", "ahora",
    "hoy", "ayer", "mañana", "siempre", "nunca", "jamas",
}


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ü", "u").replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _stem(tokens: list[str]) -> list[str]:
    stems = []
    for t in tokens:
        if t in STEMMAP:
            stems.append(STEMMAP[t])
        elif t.endswith("os") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("as") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("es") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("ar") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("er") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("ir") and len(t) > 3:
            stems.append(t[:-2])
        elif t.endswith("ando") and len(t) > 4:
            stems.append(t[:-4])
        elif t.endswith("iendo") and len(t) > 5:
            stems.append(t[:-5])
        elif t.endswith("cion") and len(t) > 4:
            stems.append(t[:-4])
        elif t.endswith("sion") and len(t) > 4:
            stems.append(t[:-4])
        elif t.endswith("miento") and len(t) > 6:
            stems.append(t[:-6])
        elif t.endswith("dad") and len(t) > 3:
            stems.append(t[:-3])
        elif t.endswith("tad") and len(t) > 3:
            stems.append(t[:-3])
        elif t.endswith("tud") and len(t) > 3:
            stems.append(t[:-3])
        else:
            stems.append(t)
    return stems


def _tokenizar_y_stem(texto: str) -> list[str]:
    normalizado = _normalizar(texto)
    tokens = [t for t in normalizado.split() if t not in STOPWORDS and (len(t) > 1 or t.isdigit())]
    return _stem(tokens)


def _expandir_con_sinonimos(tokens: list[str]) -> set[str]:
    resultado = set(tokens)
    for t in tokens:
        raiz = t
        resultado.add(raiz)
        raiz_stem = _stem([raiz])[0]
        if raiz_stem != raiz:
            resultado.add(raiz_stem)
        sinonimos = SINONIMOS.get(raiz, [])
        for s in sinonimos:
            s_norm = _normalizar(s)
            resultado.add(s_norm)
            s_stem = _stem([s_norm])[0]
            if s_stem != s_norm:
                resultado.add(s_stem)
    return resultado


def _extraer_keywords(texto: str) -> set[str]:
    tokens = _tokenizar_y_stem(texto)
    return _expandir_con_sinonimos(tokens)


def match_intencion(texto_usuario: str, opciones: list[dict]) -> Optional[int]:
    if not opciones:
        return None
    keywords_usuario = _extraer_keywords(texto_usuario)
    if not keywords_usuario:
        return None

    keywords_opciones = []
    for opcion in opciones:
        kws = _extraer_keywords(opcion["texto"])
        keywords_opciones.append(kws)

    mejor_idx: Optional[int] = None
    mejor_puntaje = 0

    for i, kws_opcion in enumerate(keywords_opciones):
        if not kws_opcion:
            continue
        coincidencias = keywords_usuario & kws_opcion
        n_coincidencias = len(coincidencias)
        if n_coincidencias == 0:
            continue
        puntaje = n_coincidencias / max(len(coincidencias | (kws_opcion - keywords_usuario)), 1)
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_idx = i

    if mejor_idx is not None and mejor_puntaje > 0:
        return mejor_idx
    return None


_NUMEROS = {
    "primero": 0, "primera": 0, "1": 0, "uno": 0,
    "segundo": 1, "segunda": 1, "2": 1, "dos": 1,
    "tercero": 2, "tercera": 2, "3": 2, "tres": 2,
    "cuarto": 3, "cuarta": 3, "4": 3, "cuatro": 3,
    "quinto": 4, "quinta": 4, "5": 4, "cinco": 4,
}


def match_numero(texto: str, opciones: list[dict]) -> Optional[int]:
    if not opciones:
        return None
    normalizado = _normalizar(texto).strip()
    if normalizado in _NUMEROS:
        idx = _NUMEROS[normalizado]
        if 0 <= idx < len(opciones):
            return idx
    tokens = _tokenizar_y_stem(texto)
    for t in tokens:
        if t in _NUMEROS:
            idx = _NUMEROS[t]
            if 0 <= idx < len(opciones):
                return idx
    if "opcion" in tokens or "opcion" in normalizado:
        for t in tokens:
            if t.isdigit():
                idx = int(t) - 1
                if 0 <= idx < len(opciones):
                    return idx
    return None
