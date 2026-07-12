import logging
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlparse, parse_qs

import customtkinter as ctk
from spotipy.oauth2 import SpotifyOAuth

from chatbot import MotorFSM, SesionSBC
from chatbot import spotify
from chatbot.frases import (
    construir_mensaje_confirmacion,
    construir_mensaje_diagnostico,
    construir_mensaje_transicion,
)

logger = logging.getLogger(__name__)

COLOR_USUARIO = "#3498DB"
COLOR_BOT = "#E8F1F5"
ANCHO_VENTANA = 450
ALTO_VENTANA = 650
DELAY_MS = 400
OAUTH_HOST = "127.0.0.1"
OAUTH_PORT = 8888

_callback_code: Optional[str] = None
_callback_event = threading.Event()


class _DesktopOAuthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        global _callback_code
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            if code:
                _callback_code = code
                _callback_event.set()
            self._responder_exito()
        except Exception as e:
            logger.error(f"Error en callback OAuth: {e}")
            self._responder_error()

    def _responder_exito(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            "<!DOCTYPE html>"
            "<html><head><meta charset='utf-8'>"
            "<title>Autenticación completada</title>"
            "<style>"
            "body{font-family:sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#f0f8ff;}"
            ".card{background:white;padding:2rem;border-radius:16px;"
            "box-shadow:0 4px 20px rgba(0,0,0,0.1);text-align:center;}"
            "h1{color:#2ecc71;}p{color:#555;}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>✅ Autenticación completada</h1>"
            "<p>Tu cuenta de Spotify se ha conectado correctamente.</p>"
            "<p>Ya puedes volver a la aplicación.</p>"
            "</div></body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def _responder_error(self) -> None:
        self.send_response(400)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            "<!DOCTYPE html>"
            "<html><head><meta charset='utf-8'>"
            "<title>Error de autenticación</title>"
            "<style>"
            "body{font-family:sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#fff5f5;}"
            ".card{background:white;padding:2rem;border-radius:16px;"
            "box-shadow:0 4px 20px rgba(0,0,0,0.1);text-align:center;}"
            "h1{color:#e74c3c;}p{color:#555;}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>❌ Error de autenticación</h1>"
            "<p>No se pudo completar la autenticación con Spotify.</p>"
            "<p>Intenta de nuevo desde la aplicación.</p>"
            "</div></body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args) -> None:
        logger.debug(f"OAuth Server: {format % args}")


class ChatbotSBCApp:

    def __init__(self) -> None:
        self.sesion = SesionSBC()
        self.motor = MotorFSM(self.sesion)
        self.sp: Optional[spotipy.Spotify] = None
        self.token_spotify: Optional[str] = None
        self._construir_gui()
        self._iniciar_conversacion()

    def _construir_gui(self) -> None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.title("Musicoterapia SBC")
        self.ventana.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.ventana.resizable(False, False)

        self._frame_superior = ctk.CTkFrame(self.ventana, height=60, fg_color="transparent")
        self._frame_superior.pack(fill="x", padx=10, pady=(10, 0))

        self._btn_spotify = ctk.CTkButton(
            self._frame_superior,
            text="Iniciar sesión con Spotify",
            command=self._iniciar_sesion_spotify,
            fg_color="#1DB954",
            hover_color="#1AA34A",
            text_color="white",
            corner_radius=20,
            height=35,
        )
        self._btn_spotify.pack(side="right", padx=(0, 5))

        self._btn_reiniciar = ctk.CTkButton(
            self._frame_superior,
            text="Reiniciar",
            command=self._reiniciar_diagnostico,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="white",
            corner_radius=20,
            height=35,
            width=90,
        )
        self._btn_reiniciar.pack(side="left", padx=(5, 0))

        self._chat_frame = ctk.CTkFrame(self.ventana, fg_color="transparent")
        self._chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._chat = ctk.CTkTextbox(
            self._chat_frame,
            wrap="word",
            state="disabled",
            fg_color="white",
            text_color="black",
            font=("Segoe UI", 13),
            corner_radius=12,
            border_width=1,
            border_color="#DDD",
        )
        self._chat.pack(fill="both", expand=True)

        self._opciones_frame = ctk.CTkFrame(self.ventana, fg_color="transparent", height=120)
        self._opciones_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._botones_dinamicos: list[ctk.CTkButton] = []

    def _agregar_mensaje(self, texto: str, es_usuario: bool = False) -> None:
        def insertar() -> None:
            self._chat.configure(state="normal")
            tag = "usuario" if es_usuario else "bot"
            color = COLOR_USUARIO if es_usuario else COLOR_BOT
            texto_color = "white" if es_usuario else "black"
            nombre = "Tú" if es_usuario else "Asistente"
            self._chat.insert("end", f"{nombre}:\n", (f"nombre_{tag}",))
            self._chat.insert("end", f"{texto}\n\n", (tag,))
            self._chat.tag_config(tag, lmargin1=20, foreground=texto_color)
            self._chat.see("end")
            self._chat.configure(state="disabled")

        self.ventana.after(DELAY_MS, insertar)

    def _agregar_mensaje_con_efecto(self, texto: str, es_usuario: bool = False) -> None:
        threading.Thread(target=self._simular_escritura, args=(texto, es_usuario), daemon=True).start()

    def _simular_escritura(self, texto: str, es_usuario: bool) -> None:
        import time
        time.sleep(DELAY_MS / 1000)
        self.ventana.after(0, lambda: self._agregar_mensaje(texto, es_usuario))

    def _mostrar_opciones(self, opciones: list[dict]) -> None:
        self._limpiar_botones()
        for i, opcion in enumerate(opciones):
            btn = ctk.CTkButton(
                self._opciones_frame,
                text=opcion["texto"],
                command=lambda idx=i: self._seleccionar_opcion(idx),
                fg_color=COLOR_USUARIO,
                hover_color="#2980B9",
                text_color="white",
                corner_radius=20,
                height=40,
                anchor="w",
            )
            btn.pack(fill="x", padx=5, pady=3)
            self._botones_dinamicos.append(btn)

    def _limpiar_botones(self) -> None:
        for btn in self._botones_dinamicos:
            btn.destroy()
        self._botones_dinamicos.clear()

    def _iniciar_conversacion(self) -> None:
        mensaje = self.motor.obtener_pregunta()
        self._agregar_mensaje_con_efecto(mensaje)
        opciones = self.motor.obtener_opciones()
        if opciones:
            self._mostrar_opciones(opciones)

    def _seleccionar_opcion(self, indice: int) -> None:
        opcion = self.motor.obtener_info_opcion(indice)
        if not opcion:
            return
        texto_opcion = opcion["texto"]
        self._agregar_mensaje(texto_opcion, es_usuario=True)
        destino = self.motor.transicionar(indice)
        if not destino:
            return
        nodo_origen = self.motor.obtener_nodo_actual()
        if hasattr(self, '_nodo_anterior'):
            confirmacion = construir_mensaje_confirmacion(
                self._nodo_anterior, self.sesion, texto_opcion
            )
            self._agregar_mensaje_con_efecto(confirmacion)
        self._nodo_anterior = nodo_origen

        if self.motor.es_nodo_hoja():
            self._procesar_nodo_hoja()
        else:
            self._procesar_nodo_decision()

    def _procesar_nodo_decision(self) -> None:
        mensaje = self.motor.obtener_pregunta()
        self._agregar_mensaje_con_efecto(mensaje)
        opciones = self.motor.obtener_opciones()
        self._mostrar_opciones(opciones)

    def _procesar_nodo_hoja(self) -> None:
        self._limpiar_botones()
        diagnostico = self.motor.obtener_diagnostico()
        self._agregar_mensaje_con_efecto(diagnostico)
        self._ejecutar_spotify()

        btn_reiniciar = ctk.CTkButton(
            self._opciones_frame,
            text="Realizar nuevo diagnóstico",
            command=self._reiniciar_diagnostico,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            text_color="white",
            corner_radius=20,
            height=45,
        )
        btn_reiniciar.pack(fill="x", padx=5, pady=5)
        self._botones_dinamicos.append(btn_reiniciar)

    def _ejecutar_spotify(self) -> None:
        nodo = self.motor.obtener_nodo_actual()
        if not nodo.get("spotify_query"):
            return

        threading.Thread(target=self._resolver_playlist_async, daemon=True).start()

    def _resolver_playlist_async(self) -> None:
        nodo = self.motor.obtener_nodo_actual()
        resultado = spotify.resolver_playlist(nodo)
        if resultado is None:
            msg = (
                "No pude obtener la playlist en este momento. "
                "Puedes intentarlo de nuevo más tarde."
            )
            self.ventana.after(0, lambda: self._agregar_mensaje(msg))
            return

        nombre = resultado.get("nombre", "Playlist recomendada")
        url = resultado.get("url", "")
        desc = resultado.get("descripcion", "")

        mensaje_playlist = (
            f"🎵 **Playlist recomendada**: {nombre}\n\n"
            f"{desc}\n\n"
            f"🔗 {url}"
        )
        self.ventana.after(0, lambda: self._agregar_mensaje(mensaje_playlist))

        if self.token_spotify:
            self._intentar_reproduccion(resultado)

    def _intentar_reproduccion(self, playlist: dict) -> None:
        try:
            sp = spotify.crear_cliente(self.token_spotify)
            uri = f"spotify:playlist:{playlist['id']}"
            resultado = spotify.reproducir_playlist(sp, uri)
            if resultado == "ok":
                self.ventana.after(0, lambda: self._agregar_mensaje(
                    "Reproduciendo en tu dispositivo activo 🎧"
                ))
                return
            elif resultado == "free_account":
                self._mostrar_enlace_spotify(playlist, "Cuenta Free")
            elif resultado == "no_device":
                self._mostrar_sin_dispositivo(playlist)
            else:
                self._mostrar_enlace_spotify(playlist, "Error")
        except Exception as e:
            logger.error(f"Error reproducción: {e}")
            self._mostrar_enlace_spotify(playlist, "Error")

    def _mostrar_enlace_spotify(self, playlist: dict, motivo: str = "") -> None:
        url = playlist.get("url", "")
        nombre = playlist.get("nombre", "Playlist")
        if url:
            msg = f"🔗 **{nombre}**\n{url}"
            self.ventana.after(0, lambda: self._agregar_mensaje(msg))

    def _mostrar_sin_dispositivo(self, playlist: dict) -> None:
        url = playlist.get("url", "")
        nombre = playlist.get("nombre", "Playlist")
        msg = (
            "No encontré un dispositivo de Spotify activo. "
            "Abre Spotify en tu celular o computadora, "
            "selecciona una canción para activar el dispositivo, "
            "y vuelve aquí para intentar de nuevo."
        )
        self.ventana.after(0, lambda: self._agregar_mensaje(msg))
        self._mostrar_enlace_spotify(playlist)

    def _iniciar_sesion_spotify(self) -> None:
        global _callback_code, _callback_event
        _callback_code = None
        _callback_event.clear()
        try:
            servidor = HTTPServer((OAUTH_HOST, OAUTH_PORT), _DesktopOAuthHandler)
            hilo_servidor = threading.Thread(
                target=servidor.serve_forever, daemon=True
            )
            hilo_servidor.start()
            oauth = spotify.crear_oauth()
            auth_url = oauth.get_authorize_url()
            webbrowser.open(auth_url)
            self._agregar_mensaje(
                "Se ha abierto el navegador para que autorices la conexión con Spotify. "
                "Después de autorizar, vuelve aquí."
            )
            threading.Thread(
                target=self._esperar_callback_oauth,
                args=(servidor, oauth),
                daemon=True,
            ).start()
        except OSError:
            self._agregar_mensaje(
                "El puerto 8888 ya está en uso. "
                "Cierra otros procesos y vuelve a intentarlo."
            )
        except Exception as e:
            logger.error(f"Error al iniciar sesión Spotify: {e}")
            self._agregar_mensaje(
                "Hubo un error al iniciar la sesión de Spotify. "
                "Verifica tus credenciales en el archivo .env"
            )

    def _esperar_callback_oauth(self, servidor: HTTPServer, oauth: SpotifyOAuth) -> None:
        global _callback_code, _callback_event
        if _callback_event.wait(timeout=180):
            try:
                resultado = oauth.get_access_token(_callback_code, as_dict=True)
                if isinstance(resultado, dict):
                    self.token_spotify = resultado["access_token"]
                else:
                    self.token_spotify = resultado
                self.ventana.after(0, lambda: self._agregar_mensaje(
                    "✅ Sesión de Spotify iniciada correctamente."
                ))
            except Exception as e:
                logger.error(f"Error al obtener token: {e}")
                self.ventana.after(0, lambda: self._agregar_mensaje(
                    "Error al obtener el token de Spotify. Intenta de nuevo."
                ))
        else:
            self.ventana.after(0, lambda: self._agregar_mensaje(
                "Tiempo de espera agotado. "
                "Vuelve a intentar iniciar sesión."
            ))
        servidor.shutdown()

    def _reiniciar_diagnostico(self) -> None:
        self.motor.reiniciar()
        self._limpiar_botones()
        self._nodo_anterior = None
        self._chat.configure(state="normal")
        self._chat.delete("1.0", "end")
        self._chat.configure(state="disabled")
        self._iniciar_conversacion()

    def ejecutar(self) -> None:
        self.ventana.mainloop()
