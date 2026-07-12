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
    construir_mensaje_empatico,
    construir_clarificacion_empatica,
    construir_mensaje_feedback,
)
from chatbot.emociones import detectar_emocion

logger = logging.getLogger(__name__)

SKBG = "#F2EBE1"
SKCARD = "#FBF8F3"
SKPRIMARY = "#8B6F47"
SKAMBER = "#D4933A"
SKGOLD_HOVER = "#BA7D2E"
SKESPRESSO = "#3D2B1F"
SKBORDER = "#C4B59E"
SKGREEN = "#2D8A4E"
SKGREEN_HOVER = "#23703F"
SKRED = "#B84A3A"
SKRED_HOVER = "#9C3D2F"
SKINPUT_BG = "#FFFFFF"
SKINPUT_BORDER = "#D0C4B0"
SKSHADOW = "#D5C9B8"

ANCHO_VENTANA = 480
ALTO_VENTANA = 680
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
            "<title>Conexión exitosa</title>"
            "<style>"
            "body{font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#F2EBE1;}"
            ".card{background:#FBF8F3;padding:2.5rem;border-radius:20px;"
            "box-shadow:8px 8px 20px rgba(139,111,71,0.15),"
            "-4px -4px 12px rgba(255,255,255,0.7);text-align:center;max-width:400px;}"
            "h1{color:#D4933A;font-weight:600;margin:0 0 0.5rem 0;}"
            "p{color:#7A6A5A;margin:0;line-height:1.6;}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>Conexión exitosa</h1>"
            "<p>Tu cuenta de Spotify se ha vinculado correctamente.<br>"
            "Ya puedes volver a la aplicación y continuar.</p>"
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
            "body{font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#F2EBE1;}"
            ".card{background:#FBF8F3;padding:2.5rem;border-radius:20px;"
            "box-shadow:8px 8px 20px rgba(139,111,71,0.15),"
            "-4px -4px 12px rgba(255,255,255,0.7);text-align:center;max-width:400px;}"
            "h1{color:#B84A3A;font-weight:600;margin:0 0 0.5rem 0;}"
            "p{color:#7A6A5A;margin:0;line-height:1.6;}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>Error de autenticación</h1>"
            "<p>No se pudo completar la conexión con Spotify.<br>"
            "Intenta de nuevo.</p>"
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
        self._procesando = False
        self._fallos_consecutivos = 0
        self._esperando_feedback = False
        self._construir_gui()
        self._iniciar_conversacion()

    def _construir_gui(self) -> None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.title("Antidepresión Sonora — Musicoterapia")
        self.ventana.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.ventana.resizable(False, False)
        self.ventana.configure(fg_color=SKBG)

        self._construir_barra_superior()
        self._construir_chat()
        self._construir_input()

    def _construir_barra_superior(self) -> None:
        contenedor = ctk.CTkFrame(
            self.ventana, height=72, fg_color=SKCARD,
            corner_radius=16, border_width=1, border_color=SKBORDER,
        )
        contenedor.pack(fill="x", padx=14, pady=(14, 0))
        contenedor.pack_propagate(False)

        marco_interno = ctk.CTkFrame(contenedor, fg_color="transparent")
        marco_interno.pack(fill="both", expand=True, padx=14, pady=10)

        ctk.CTkLabel(
            marco_interno, text="Antidepresión Sonora",
            font=("Georgia", 18, "bold"), text_color=SKPRIMARY,
        ).pack(side="left")

        self._btn_spotify = ctk.CTkButton(
            marco_interno,
            text="Conectar Spotify",
            command=self._iniciar_sesion_spotify,
            fg_color=SKGREEN,
            hover_color=SKGREEN_HOVER,
            text_color="white",
            corner_radius=22,
            height=36,
            font=("Segoe UI", 12, "bold"),
            border_width=1,
            border_color="#1E6B38",
        )
        self._btn_spotify.pack(side="right", padx=(6, 0))

        self._btn_reiniciar = ctk.CTkButton(
            marco_interno,
            text="Nuevo",
            command=self._reiniciar_diagnostico,
            fg_color=SKRED,
            hover_color=SKRED_HOVER,
            text_color="white",
            corner_radius=22,
            height=36,
            width=80,
            font=("Segoe UI", 12, "bold"),
            border_width=1,
            border_color="#8E3B2E",
        )
        self._btn_reiniciar.pack(side="right", padx=(0, 6))

    def _construir_chat(self) -> None:
        self._chat_frame = ctk.CTkFrame(
            self.ventana, fg_color=SKCARD,
            corner_radius=16, border_width=1, border_color=SKBORDER,
        )
        self._chat_frame.pack(fill="both", expand=True, padx=14, pady=(12, 6))

        self._chat = ctk.CTkTextbox(
            self._chat_frame,
            wrap="word",
            state="disabled",
            fg_color="#FDFBF7",
            text_color=SKESPRESSO,
            font=("Segoe UI", 13),
            corner_radius=12,
            border_width=0,
            scrollbar_button_color=SKPRIMARY,
            scrollbar_button_hover_color=SKPRIMARY,
        )
        self._chat.pack(fill="both", expand=True, padx=10, pady=10)

        self._chat.tag_config("usuario_nombre", foreground=SKAMBER)
        self._chat.tag_config("bot_nombre", foreground=SKPRIMARY)
        self._chat.tag_config("usuario", lmargin1=20, foreground=SKESPRESSO)
        self._chat.tag_config("bot", lmargin1=20, foreground="#5A4A3A")

    def _construir_input(self) -> None:
        contenedor = ctk.CTkFrame(
            self.ventana, fg_color="transparent", height=56,
        )
        contenedor.pack(fill="x", padx=14, pady=(0, 14))
        contenedor.pack_propagate(False)

        marco_input = ctk.CTkFrame(
            contenedor, fg_color=SKCARD,
            corner_radius=28, border_width=1, border_color=SKINPUT_BORDER,
        )
        marco_input.pack(fill="both", expand=True)

        self._entry = ctk.CTkEntry(
            marco_input,
            placeholder_text="Escribe cómo te sientes...",
            font=("Segoe UI", 13),
            fg_color="transparent",
            text_color=SKESPRESSO,
            border_width=0,
            corner_radius=28,
            height=36,
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(18, 6), pady=8)
        self._entry.bind("<Return>", lambda e: self._enviar_texto())

        self._btn_enviar = ctk.CTkButton(
            marco_input,
            text="Enviar",
            command=self._enviar_texto,
            fg_color=SKAMBER,
            hover_color=SKGOLD_HOVER,
            text_color="white",
            corner_radius=28,
            height=36,
            width=80,
            font=("Segoe UI", 13, "bold"),
            border_width=1,
            border_color="#B87A28",
        )
        self._btn_enviar.pack(side="right", padx=(0, 6), pady=8)

    def _enviar_texto(self) -> None:
        if self._procesando:
            return
        texto = self._entry.get().strip()
        if not texto:
            return
        self._entry.delete(0, "end")
        self._procesando = True
        threading.Thread(target=self._procesar_texto_usuario, args=(texto,), daemon=True).start()

    def _procesar_texto_usuario(self, texto: str) -> None:
        if self._esperando_feedback:
            self.sesion.feedback_recomendacion = texto
            self._agregar_mensaje(texto, es_usuario=True)
            self._esperando_feedback = False
            msg = "Gracias por tu opinión. Me ayuda a mejorar las recomendaciones para ti."
            self._agregar_mensaje_con_efecto(msg)
            self._procesando = False
            return

        resultado = self.motor.procesar_texto(texto)

        if resultado["tipo"] == "opcion":
            self._fallos_consecutivos = 0
            self.ventana.after(0, lambda: self._ejecutar_opcion(resultado["indice"]))
        elif resultado["tipo"] == "redireccion":
            self._fallos_consecutivos = 0
            self._agregar_mensaje(texto, es_usuario=True)
            self._manejar_redireccion(resultado["sugerencia"])
        else:
            self._fallos_consecutivos += 1
            self._agregar_mensaje(texto, es_usuario=True)
            self._pedir_clarificacion()

    def _manejar_redireccion(self, sugerencia: dict) -> None:
        destinos = sugerencia.get("destinos", [])
        opciones = self.motor.obtener_opciones()
        nombres = []
        indices = []
        for i, o in enumerate(opciones):
            if o.get("destino", "") in destinos:
                nombres.append(o["texto"].split("(")[0].strip().lower())
                indices.append(i)
        if nombres:
            msg = (
                f"Por cómo te expresas, parece que estás experimentando "
                f"algo más de tipo emocional. "
                f"¿Te parece que {nombres[0]} describe mejor lo que sientes?"
            )
            if len(nombres) > 1:
                opciones_str = " o ".join(nombres)
                msg = (
                    f"Por cómo te expresas, lo que cuentas parece más cercano a "
                    f"{opciones_str}. ¿Cuál resuena más contigo?"
                )
            self._agregar_mensaje_con_efecto(msg)
        else:
            self._pedir_clarificacion()
        self._procesando = False

    def _pedir_clarificacion(self) -> None:
        fallos = self._fallos_consecutivos
        nodo = self.motor.obtener_nodo_actual()
        opciones = nodo.get("opciones", [])
        if not opciones:
            self._procesando = False
            return

        if fallos == 1:
            empatica = construir_clarificacion_empatica(self.sesion, opciones)
            if empatica:
                msg = empatica
            else:
                mensaje_empatico = self.motor.obtener_mensaje_empatico()
                if mensaje_empatico:
                    msg = mensaje_empatico
                else:
                    msg = "Cuéntame un poco más para entenderte mejor."
        elif fallos == 2:
            textos = [o["texto"].split("(")[0].strip().lower() for o in opciones]
            n = len(textos)
            emotion = self.sesion.emotion_principal
            if emotion != "neutral":
                if n == 1:
                    msg = f"Por lo que dices, ¿{textos[0]} describe lo que sientes?"
                elif n == 2:
                    msg = f"¿Lo que sientes se parece más a {textos[0]} o a {textos[1]}?"
                else:
                    msg = f"¿Lo que sientes se acerca más a {textos[0]}, {textos[1]} o {textos[2]}?"
            else:
                if n == 1:
                    msg = f"¿Te parece que {textos[0]} describe lo que sientes?"
                elif n == 2:
                    msg = f"Déjame preguntarte de otra forma. ¿Lo que sientes es más {textos[0]} o {textos[1]}?"
                else:
                    msg = f"Déjame preguntarte de otra forma. ¿Lo que sientes es más {textos[0]}, {textos[1]} o {textos[2]}?"
        else:
            palabras_clave = []
            for o in opciones:
                parentesis = o["texto"].split("(")
                if len(parentesis) > 1:
                    palabras = parentesis[1].rstrip(")").split(",")
                    palabras_clave.extend(p.strip() for p in palabras[:2])
            if palabras_clave:
                ejemplos = ", ".join(palabras_clave[:4])
                msg = (
                    "Para ayudarte mejor, dime si alguna de estas palabras "
                    f"resuena con lo que sientes: {ejemplos}."
                )
            else:
                msg = "Cuéntame con tus palabras cómo te sientes."
        self._agregar_mensaje_con_efecto(msg)
        self._procesando = False

    def _agregar_mensaje(self, texto: str, es_usuario: bool = False) -> None:
        def insertar() -> None:
            self._chat.configure(state="normal")
            if es_usuario:
                self._chat.insert("end", "Tú:\n", "usuario_nombre")
                self._chat.insert("end", f"{texto}\n\n", "usuario")
            else:
                self._chat.insert("end", "Asistente:\n", "bot_nombre")
                self._chat.insert("end", f"{texto}\n\n", "bot")
            self._chat.see("end")
            self._chat.configure(state="disabled")

        self.ventana.after(DELAY_MS, insertar)

    def _agregar_mensaje_con_efecto(self, texto: str, es_usuario: bool = False) -> None:
        threading.Thread(target=self._simular_escritura, args=(texto, es_usuario), daemon=True).start()

    def _simular_escritura(self, texto: str, es_usuario: bool) -> None:
        import time
        time.sleep(DELAY_MS / 1000)
        self.ventana.after(0, lambda: self._agregar_mensaje(texto, es_usuario))

    def _iniciar_conversacion(self) -> None:
        mensaje = self.motor.obtener_pregunta()
        self._agregar_mensaje_con_efecto(mensaje)

    def _ejecutar_opcion(self, indice: int) -> None:
        opcion = self.motor.obtener_info_opcion(indice)
        if not opcion:
            self._procesando = False
            return
        texto_opcion = opcion["texto"]
        self._agregar_mensaje(texto_opcion, es_usuario=True)
        destino = self.motor.transicionar(indice)
        if not destino:
            self._procesando = False
            return

        nodo_origen = self.motor.obtener_nodo_actual()
        if hasattr(self, '_nodo_anterior') and self._nodo_anterior is not None:
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
        self._procesando = False

    def _procesar_nodo_hoja(self) -> None:
        diagnostico = self.motor.obtener_diagnostico()
        self._agregar_mensaje_con_efecto(diagnostico)
        self._ejecutar_spotify()

        def mostrar_contenido():
            self._procesando = False
        self.ventana.after(0, mostrar_contenido)

    def _ejecutar_spotify(self) -> None:
        nodo = self.motor.obtener_nodo_actual()
        if not nodo.get("spotify_query"):
            return
        threading.Thread(target=self._resolver_playlist_async, daemon=True).start()

    def _resolver_playlist_async(self) -> None:
        nodo = self.motor.obtener_nodo_actual()
        resultado = spotify.resolver_playlist(nodo)
        if resultado is None:
            msg = "No pude obtener la playlist en este momento. Puedes intentarlo de nuevo más tarde."
            self.ventana.after(0, lambda: self._agregar_mensaje(msg))
            self.ventana.after(0, lambda: self._mostrar_boton_reiniciar())
            return

        nombre = resultado.get("nombre", "Playlist recomendada")
        url = resultado.get("url", "")
        desc = resultado.get("descripcion", "")

        mensaje_playlist = (
            f"Playlist recomendada: {nombre}\n\n"
            f"{desc}\n\n"
            f"Escúchala aquí: {url}"
        )
        self.ventana.after(0, lambda: self._agregar_mensaje(mensaje_playlist))
        self._resultado_playlist = resultado

        self.sesion.registrar_recomendacion(resultado)

        self.ventana.after(1500, self._mostrar_acciones_playlist)
        self.ventana.after(1000, self._preguntar_feedback)

    def _mostrar_acciones_playlist(self) -> None:
        if not hasattr(self, '_resultado_playlist'):
            self._mostrar_boton_reiniciar()
            return

        url = self._resultado_playlist.get("url", "")

        def abrir_spotify():
            if url:
                webbrowser.open(url)

        def reproducir():
            if self.token_spotify:
                threading.Thread(target=lambda: self._intentar_reproduccion(self._resultado_playlist), daemon=True).start()
            elif url:
                webbrowser.open(url)

        def nuevo():
            self._reiniciar_diagnostico()

        marco = ctk.CTkFrame(
            self._chat_frame, fg_color="transparent",
        )
        marco.pack(fill="x", padx=10, pady=(4, 8))

        if url:
            btn_abrir = ctk.CTkButton(
                marco, text="Abrir en Spotify",
                command=abrir_spotify,
                fg_color=SKGREEN, hover_color=SKGREEN_HOVER,
                text_color="white", corner_radius=22, height=40,
                font=("Segoe UI", 13, "bold"),
                border_width=1, border_color="#1E6B38",
            )
            btn_abrir.pack(fill="x", padx=5, pady=3)

        if self.token_spotify:
            btn_repro = ctk.CTkButton(
                marco, text="Reproducir ahora",
                command=reproducir,
                fg_color=SKAMBER, hover_color=SKGOLD_HOVER,
                text_color="white", corner_radius=22, height=40,
                font=("Segoe UI", 13, "bold"),
                border_width=1, border_color="#B87A28",
            )
            btn_repro.pack(fill="x", padx=5, pady=3)

        btn_nuevo = ctk.CTkButton(
            marco, text="Nuevo diagnóstico",
            command=nuevo,
            fg_color=SKPRIMARY, hover_color="#7A5F3A",
            text_color="white", corner_radius=22, height=40,
            font=("Segoe UI", 13, "bold"),
            border_width=1, border_color="#6B4F30",
        )
        btn_nuevo.pack(fill="x", padx=5, pady=3)

        self._btn_reiniciar_hoja = marco
        self._procesando = False

    def _preguntar_feedback(self) -> None:
        msg = construir_mensaje_feedback()
        self._agregar_mensaje_con_efecto(msg)
        self._esperando_feedback = True
        self._procesando = False

    def _mostrar_boton_reiniciar(self) -> None:
        if hasattr(self, '_btn_reiniciar_hoja'):
            return
        btn_reiniciar = ctk.CTkButton(
            self._chat_frame,
            text="Realizar nuevo diagnóstico",
            command=self._reiniciar_diagnostico,
            fg_color=SKGREEN,
            hover_color=SKGREEN_HOVER,
            text_color="white",
            corner_radius=22,
            height=44,
            font=("Segoe UI", 14, "bold"),
            border_width=1,
            border_color="#1E6B38",
        )
        btn_reiniciar.pack(fill="x", padx=30, pady=(0, 14))
        self._btn_reiniciar_hoja = btn_reiniciar

    def _intentar_reproduccion(self, playlist: dict) -> None:
        try:
            sp = spotify.crear_cliente(self.token_spotify)
            uri = f"spotify:playlist:{playlist['id']}"
            resultado = spotify.reproducir_playlist(sp, uri)
            if resultado == "ok":
                self.ventana.after(0, lambda: self._agregar_mensaje(
                    "Reproduciendo en tu dispositivo activo"
                ))
                return
            elif resultado == "free_account":
                pass
            elif resultado == "no_device":
                self._mostrar_sin_dispositivo(playlist)
            else:
                pass
        except Exception as e:
            logger.error(f"Error reproducción: {e}")

    def _mostrar_sin_dispositivo(self, playlist: dict) -> None:
        msg = (
            "No encontré un dispositivo de Spotify activo. "
            "Abre Spotify en tu celular o computadora, "
            "reproduce algo para activarlo, y vuelve aquí."
        )
        self.ventana.after(0, lambda: self._agregar_mensaje(msg))

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
                "Se abrió el navegador para autorizar Spotify. "
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
                "Hubo un error al iniciar sesión de Spotify. "
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
                    "Conexión con Spotify exitosa."
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
        self._nodo_anterior = None
        self._procesando = False
        self._fallos_consecutivos = 0
        self._esperando_feedback = False
        if hasattr(self, '_resultado_playlist'):
            del self._resultado_playlist
        self._chat.configure(state="normal")
        self._chat.delete("1.0", "end")
        self._chat.configure(state="disabled")
        if hasattr(self, '_btn_reiniciar_hoja'):
            self._btn_reiniciar_hoja.destroy()
            del self._btn_reiniciar_hoja
        self._iniciar_conversacion()

    def ejecutar(self) -> None:
        self.ventana.mainloop()
