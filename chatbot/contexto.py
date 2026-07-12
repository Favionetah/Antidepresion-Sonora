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

    emotion_principal: str = "neutral"
    emotion_puntajes: dict[str, float] = field(default_factory=dict)
    intensidad_emocional: str = "media"
    ultimo_texto_usuario: str = ""

    feedback_recomendacion: Optional[str] = None
    historial_recomendaciones: list[dict] = field(default_factory=list)

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
        self.emotion_principal = "neutral"
        self.emotion_puntajes.clear()
        self.intensidad_emocional = "media"
        self.ultimo_texto_usuario = ""
        self.feedback_recomendacion = None
        self.historial_recomendaciones.clear()

    def actualizar_emocion(self, resultado: dict) -> None:
        self.emotion_principal = resultado["principal"]
        self.emotion_puntajes = resultado["puntajes"]
        self.intensidad_emocional = resultado["intensidad"]

    def registrar_recomendacion(self, playlist: dict) -> None:
        self.historial_recomendaciones.append({
            "playlist": playlist,
            "timestamp": datetime.now().isoformat(),
            "feedback": None,
        })
