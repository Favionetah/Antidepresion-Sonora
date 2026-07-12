from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SesionSBC:
    nodo_actual: str = "N01"
    historial_nodos: list[str] = field(default_factory=list)
    sintomas_principales: str = ""
    rama_elegida: str = ""
    intensidad: str = ""
    intervencion_elegida: str = ""
    playlist_recomendada: Optional[dict] = None
    usuario_spotify: str = ""
    hora_inicio: datetime = field(default_factory=datetime.now)
    historial_frases_recientes: list[str] = field(default_factory=list)
    token_spotify: Optional[str] = None

    def reiniciar(self) -> None:
        self.nodo_actual = "N01"
        self.historial_nodos.clear()
        self.sintomas_principales = ""
        self.rama_elegida = ""
        self.intensidad = ""
        self.intervencion_elegida = ""
        self.playlist_recomendada = None
        self.usuario_spotify = ""
        self.hora_inicio = datetime.now()
        self.historial_frases_recientes.clear()
        self.token_spotify = None
