from typing import Optional

from .base_conocimiento import BaseConocimiento
from .contexto import SesionSBC
from .emociones import detectar_emocion, emocion_a_rama
from .frases import (
    construir_mensaje_inicial,
    construir_mensaje_confirmacion,
    construir_mensaje_diagnostico,
    construir_mensaje_transicion,
    construir_mensaje_empatico,
)
from .intenciones import match_intencion, match_numero


EMOCIONES_ESPERADAS_POR_NODO: dict[str, list[str]] = {
    "N01": ["neutral"],
    "N02": ["miedo", "neutral"],
    "N03": ["miedo", "tristeza", "neutral"],
    "N04": ["enojo", "tristeza", "neutral"],
    "N05": ["miedo"],
    "N06": ["tristeza", "neutral"],
    "N07": ["frustracion", "neutral"],
    "N08": ["miedo", "ansiedad"],
    "N09": ["enojo", "frustracion"],
    "N10": ["tristeza"],
    "N11": ["miedo"],
    "N12": ["miedo"],
    "N13": ["tristeza", "neutral"],
    "N14": ["neutral"],
    "N15": ["miedo", "neutral"],
    "N16": ["enojo", "frustracion"],
}


class MotorFSM:

    def __init__(self, sesion: SesionSBC) -> None:
        self.sesion = sesion
        self.base = BaseConocimiento()

    @property
    def estado_actual(self) -> str:
        return self.sesion.nodo_actual

    @estado_actual.setter
    def estado_actual(self, valor: str) -> None:
        self.sesion.nodo_actual = valor

    def obtener_nodo_actual(self) -> dict:
        return self.base.obtener_nodo(self.estado_actual)

    def obtener_pregunta(self) -> str:
        nodo = self.obtener_nodo_actual()
        return construir_mensaje_inicial(nodo, self.sesion)

    def obtener_opciones(self) -> list[dict]:
        nodo = self.obtener_nodo_actual()
        return nodo.get("opciones", [])

    def es_nodo_hoja(self) -> bool:
        nodo = self.obtener_nodo_actual()
        return nodo.get("esHoja", False)

    def obtener_diagnostico(self) -> str:
        nodo = self.obtener_nodo_actual()
        return construir_mensaje_diagnostico(nodo, self.sesion)

    def transicionar(self, indice_opcion: int) -> Optional[str]:
        opciones = self.obtener_opciones()
        if indice_opcion < 0 or indice_opcion >= len(opciones):
            return None
        opcion = opciones[indice_opcion]
        destino = opcion.get("destino", "")
        if not destino:
            return None
        self.sesion.historial_nodos.append(self.estado_actual)
        self.estado_actual = destino
        if self.es_nodo_hoja():
            return destino
        return destino

    def obtener_info_opcion(self, indice_opcion: int) -> Optional[dict]:
        opciones = self.obtener_opciones()
        if indice_opcion < 0 or indice_opcion >= len(opciones):
            return None
        return opciones[indice_opcion]

    def procesar_texto(self, texto: str) -> dict:
        resultado_emocion = detectar_emocion(texto)
        self.sesion.actualizar_emocion(resultado_emocion)
        self.sesion.ultimo_texto_usuario = texto

        idx = self.match_intencion(texto)
        if idx is not None:
            return {"tipo": "opcion", "indice": idx, "emocion": resultado_emocion}

        redireccion = self._evaluar_redireccion_emocional(resultado_emocion)
        if redireccion:
            return {
                "tipo": "redireccion",
                "sugerencia": redireccion,
                "emocion": resultado_emocion,
            }

        return {"tipo": "no_match", "emocion": resultado_emocion}

    def match_intencion(self, texto: str) -> Optional[int]:
        opciones = self.obtener_opciones()
        idx = match_numero(texto, opciones)
        if idx is not None:
            return idx
        return match_intencion(texto, opciones)

    def _evaluar_redireccion_emocional(self, resultado_emocion: dict) -> Optional[dict]:
        emotion = resultado_emocion["principal"]
        intensidad = resultado_emocion["intensidad"]
        if emotion == "neutral" or intensidad != "alta":
            return None

        nodo_id = self.estado_actual
        esperadas = EMOCIONES_ESPERADAS_POR_NODO.get(nodo_id, ["neutral"])
        if emotion in esperadas:
            return None

        ramas_alternativas = emocion_a_rama(emotion)
        if not ramas_alternativas or not self.es_accesible(ramas_alternativas):
            return None

        return {
            "emocion": emotion,
            "intensidad": intensidad,
            "destinos": ramas_alternativas,
        }

    def es_accesible(self, destinos: list[str]) -> bool:
        opciones = self.obtener_opciones()
        destinos_opciones = {o.get("destino", "") for o in opciones}
        for d in destinos:
            if d in destinos_opciones:
                return True
        return False

    def obtener_mensaje_empatico(self) -> Optional[str]:
        return construir_mensaje_empatico(self.sesion)

    def reiniciar(self) -> None:
        self.sesion.reiniciar()
