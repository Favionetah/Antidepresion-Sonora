from typing import Optional

from .base_conocimiento import BaseConocimiento
from .contexto import SesionSBC
from .frases import (
    construir_mensaje_inicial,
    construir_mensaje_confirmacion,
    construir_mensaje_diagnostico,
    construir_mensaje_transicion,
)


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

    def reiniciar(self) -> None:
        self.sesion.reiniciar()
