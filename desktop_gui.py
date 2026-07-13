import logging
import os
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlparse, parse_qs

import spotipy
import customtkinter as ctk
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

from chatbot import MotorFSM, SesionSBC
from chatbot import spotify
from chatbot.frases import (
    construir_mensaje_confirmacion,
    construir_mensaje_diagnostico,
)

logger = logging.getLogger(__name__)

LIGHT = {
    "bg": "#F0F4FF",
    "card": "#FFFFFF",
    "primary": "#223CCC",
    "primary_hover": "#161B8E",
    "accent": "#8D39D0",
    "accent_hover": "#7A2FB8",
    "text": "#1A1A2E",
    "text_sec": "#6B7280",
    "border": "#E2E8F0",
    "red": "#ED4563",
    "red_hover": "#D63551",
    "chat": "#F8FAFF",
    "bubble_bot": "#E8EDFF",
    "bubble_user": "#223CCC",
    "bubble_user_text": "#FFFFFF",
    "bubble_bot_text": "#1A1A2E",
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E1",
    "green": "#1DB954",
    "amber": "#D4933A",
}

DARK = {
    "bg": "#0A0F1E",
    "card": "#131A30",
    "primary": "#3B5FE0",
    "primary_hover": "#223CCC",
    "accent": "#A855F7",
    "accent_hover": "#8D39D0",
    "text": "#E8EDFF",
    "text_sec": "#94A3B8",
    "border": "#1E293B",
    "red": "#F87171",
    "red_hover": "#ED4563",
    "chat": "#0D1326",
    "bubble_bot": "#1E293B",
    "bubble_user": "#223CCC",
    "bubble_user_text": "#FFFFFF",
    "bubble_bot_text": "#E8EDFF",
    "input_bg": "#131A30",
    "input_border": "#334155",
    "green": "#1DB954",
    "amber": "#D4933A",
}

ANCHO = 520
ALTO = 720
DELAY_MS = 300
OAUTH_HOST = "127.0.0.1"
OAUTH_PORT = 8888
if getattr(sys, 'frozen', False):
    RUTA_ICONOS = os.path.join(sys._MEIPASS, "assets")
else:
    RUTA_ICONOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

_callback_code: Optional[str] = None
_callback_event = threading.Event()


class _DesktopOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            logger.error(f"OAuth error: {e}")
            self._responder_error()

    def _responder_exito(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>"
            "body{font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#F5F0FF;}"
            ".card{background:white;padding:2.5rem;border-radius:20px;"
            "box-shadow:0 4px 30px rgba(139,92,246,0.15);text-align:center;max-width:400px;}"
            "h1{color:#059669;font-weight:600;margin:0 0 0.5rem 0;}"
            "p{color:#6B7280;margin:0;line-height:1.6;}"
            "</style></head><body>"
            "<div class='card'><h1>Conexión exitosa</h1>"
            "<p>Tu cuenta de Spotify se ha vinculado correctamente.<br>"
            "Ya puedes volver a la aplicación.</p></div></body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def _responder_error(self):
        self.send_response(400)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>"
            "body{font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;"
            "align-items:center;height:100vh;margin:0;background:#F5F0FF;}"
            ".card{background:white;padding:2.5rem;border-radius:20px;"
            "box-shadow:0 4px 30px rgba(139,92,246,0.15);text-align:center;max-width:400px;}"
            "h1{color:#DC2626;font-weight:600;margin:0 0 0.5rem 0;}"
            "p{color:#6B7280;margin:0;line-height:1.6;}"
            "</style></head><body>"
            "<div class='card'><h1>Error de autenticación</h1>"
            "<p>No se pudo completar la conexión con Spotify.<br>"
            "Intenta de nuevo.</p></div></body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        logger.debug(f"OAuth: {format % args}")


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self._theme = LIGHT
        self.geometry("400x300+{}+{}".format(
            parent.winfo_screenwidth() // 2 - 200,
            parent.winfo_screenheight() // 2 - 150,
        ))
        self.configure(fg_color=self._theme["bg"])
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Logo
        logo_path = os.path.join(RUTA_ICONOS, "splash_logo.png")
        if os.path.exists(logo_path):
            pil = Image.open(logo_path).resize((60, 60), Image.LANCZOS)
            self._ctk_logo = ctk.CTkImage(pil, size=(60, 60))
            lbl_logo = ctk.CTkLabel(self, image=self._ctk_logo, text="")
            lbl_logo.pack(expand=True, pady=(40, 0))

        ctk.CTkLabel(
            self,
            text="Antidepresión Sonora",
            font=("Raleway", 22, "bold"),
            text_color=self._theme["primary"],
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self,
            text="Cargando tu experiencia musical...",
            font=("Segoe UI", 12),
            text_color=self._theme["text_sec"],
        ).pack(pady=(0, 20))

        self._barra = ctk.CTkProgressBar(
            self,
            width=250,
            height=4,
            fg_color=self._theme["border"],
            progress_color=self._theme["primary"],
            corner_radius=2,
        )
        self._barra.pack(pady=(0, 30))
        self._barra.set(0)

        self._animar_barra()
        self.after(2200, self.destroy)

    def _animar_barra(self):
        def animar(paso=0):
            if paso > 100:
                return
            self._barra.set(paso / 100)
            self.after(20, lambda: animar(paso + 2))
        animar()


def _cargar_icono(nombre: str, size: int = 20) -> Optional[ctk.CTkImage]:
    ruta = os.path.join(RUTA_ICONOS, f"{nombre}.png")
    if not os.path.exists(ruta):
        return None
    try:
        pil = Image.open(ruta).resize((size, size), Image.LANCZOS)
        return ctk.CTkImage(pil, size=(size, size))
    except Exception as e:
        logger.warning(f"No se pudo cargar icono {nombre}: {e}")
        return None


class ChatbotSBCApp:
    def __init__(self):
        self._dark = False
        self._t = dict(LIGHT)
        self.sesion = SesionSBC()
        self.motor = MotorFSM(self.sesion)
        self.sp: Optional[spotipy.Spotify] = None
        self.token_spotify: Optional[str] = None
        self._procesando = False
        self._fallos_consecutivos = 0
        self._esperando_feedback = False
        self._botones_opciones_actuales = []
        self._iconos: dict[str, ctk.CTkImage] = {}
        self._typing_activo = False
        self._construir_gui()
        self._mostrar_splash()

    def _mostrar_splash(self):
        splash = SplashScreen(self.ventana)
        splash.wait_window()
        self._iniciar_conversacion()

    def _construir_gui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._cargar_iconos()

        self.ventana = ctk.CTk()
        self.ventana.title("Antidepresión Sonora — Musicoterapia")
        self.ventana.geometry(f"{ANCHO}x{ALTO}")
        self.ventana.resizable(False, False)
        self.ventana.configure(fg_color=self._t["bg"])

        self._construir_barra_superior()
        self._construir_chat()
        self._construir_input()

    def _cargar_iconos(self):
        for nombre in ("spotify", "send", "retry", "disconnect", "new", "check", "moon", "sun"):
            icono = _cargar_icono(nombre)
            if icono:
                self._iconos[nombre] = icono

    def _aplicar_tema(self):
        self._t = dict(DARK if self._dark else LIGHT)
        modo = "dark" if self._dark else "light"
        ctk.set_appearance_mode(modo)

        self.ventana.configure(fg_color=self._t["bg"])
        self._barra_sup.configure(fg_color=self._t["card"], border_color=self._t["border"])
        self._chat_frame.configure(fg_color=self._t["card"], border_color=self._t["border"])
        self._chat.configure(fg_color=self._t["chat"], text_color=self._t["text"])
        self._input_frame.configure(fg_color=self._t["card"], border_color=self._t["input_border"])
        self._entry.configure(text_color=self._t["text"], placeholder_text_color=self._t["text_sec"])
        self._btn_enviar.configure(
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"]
        )
        self._btn_spotify.configure(
            fg_color=self._t["green"], hover_color=self._t["accent_hover"],
            border_color=self._t["accent_hover"]
        )
        self._btn_reiniciar.configure(
            fg_color=self._t["red"], hover_color=self._t["red_hover"],
            border_color=self._t["red_hover"]
        )

        if self.token_spotify:
            self._actualizar_btn_conectado(self._nombre_spotify if hasattr(self, '_nombre_spotify') else "Spotify")

        self._btn_tema.configure(
            image=self._iconos.get("sun" if self._dark else "moon"),
            fg_color=self._t["card"], hover_color=self._t["border"],
        )

    def _toggle_tema(self):
        self._dark = not self._dark
        self._aplicar_tema()

    def _construir_barra_superior(self):
        self._barra_sup = ctk.CTkFrame(
            self.ventana, height=72, fg_color=self._t["card"],
            corner_radius=16, border_width=1, border_color=self._t["border"],
        )
        self._barra_sup.pack(fill="x", padx=14, pady=(14, 0))
        self._barra_sup.pack_propagate(False)

        marco = ctk.CTkFrame(self._barra_sup, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=14, pady=10)

        ctk.CTkLabel(
            marco, text="Antidepresión Sonora",
            font=("Raleway", 16, "bold"), text_color=self._t["primary"],
        ).pack(side="left")

        self._btn_tema = ctk.CTkButton(
            marco, text="", width=36, height=36,
            image=self._iconos.get("moon"),
            command=self._toggle_tema,
            fg_color=self._t["card"], hover_color=self._t["border"],
            corner_radius=18,
        )
        self._btn_tema.pack(side="right", padx=(4, 0))

        self._btn_spotify = ctk.CTkButton(
            marco, text="Spotify", width=80, height=36,
            command=self._iniciar_sesion_spotify,
            fg_color=self._t["green"], hover_color=self._t["accent_hover"],
            text_color="white", corner_radius=22, font=("Segoe UI", 11, "bold"),
            border_width=1, border_color=self._t["accent_hover"],
        )
        self._btn_spotify.pack(side="right", padx=(4, 0))

        self._btn_reiniciar = ctk.CTkButton(
            marco, text="Nuevo", width=80, height=36,
            command=self._reiniciar_diagnostico,
            fg_color=self._t["red"], hover_color=self._t["red_hover"],
            corner_radius=18,
        )
        self._btn_reiniciar.pack(side="right", padx=(0, 0))

    def _construir_chat(self):
        self._chat_frame = ctk.CTkFrame(
            self.ventana, fg_color=self._t["card"],
            corner_radius=16, border_width=1, border_color=self._t["border"],
        )
        self._chat_frame.pack(fill="both", expand=True, padx=14, pady=(10, 6))

        self._chat = ctk.CTkTextbox(
            self._chat_frame,
            wrap="word", state="disabled",
            fg_color=self._t["chat"], text_color=self._t["text"],
            font=("Segoe UI", 13),
            corner_radius=12, border_width=0,
            scrollbar_button_color=self._t["primary"],
            scrollbar_button_hover_color=self._t["primary_hover"],
        )
        self._chat.pack(fill="both", expand=True, padx=8, pady=8)

        self._chat.tag_config("bubble_bot", lmargin1=20, lmargin2=14, rmargin=80,
                              foreground=self._t["bubble_bot_text"],
                              spacing1=6, spacing3=6)
        self._chat.tag_config("bubble_user", lmargin1=80, lmargin2=76, rmargin=16,
                              foreground=self._t["bubble_user_text"],
                              spacing1=6, spacing3=6, justify="right")
        self._chat.tag_config("typing", lmargin1=20, rmargin=80,
                              foreground=self._t["text_sec"], spacing1=2, spacing3=2)

    def _construir_input(self):
        contenedor = ctk.CTkFrame(self.ventana, fg_color="transparent", height=56)
        contenedor.pack(fill="x", padx=14, pady=(0, 14))
        contenedor.pack_propagate(False)

        self._input_frame = ctk.CTkFrame(
            contenedor, fg_color=self._t["card"],
            corner_radius=28, border_width=1, border_color=self._t["input_border"],
        )
        self._input_frame.pack(fill="both", expand=True)

        self._entry = ctk.CTkEntry(
            self._input_frame,
            placeholder_text="Describe cómo te sientes...",
            font=("Segoe UI", 13),
            fg_color="transparent", text_color=self._t["text"],
            border_width=0, corner_radius=28, height=36,
            placeholder_text_color=self._t["text_sec"],
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(18, 6), pady=8)
        self._entry.bind("<Return>", lambda e: self._enviar_texto())

        self._btn_enviar = ctk.CTkButton(
            self._input_frame, text="", width=36, height=36,
            image=self._iconos.get("send"),
            command=self._enviar_texto,
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
            corner_radius=18,
        )
        self._btn_enviar.pack(side="right", padx=(0, 6), pady=6)

    def _agregar_mensaje(self, texto: str, es_usuario: bool = False):
        if self._typing_activo:
            self._ocultar_typing()

        def insertar():
            self._chat.configure(state="normal")
            tag = "bubble_user" if es_usuario else "bubble_bot"
            if es_usuario:
                self._chat.insert("end", f"{texto}\n", tag)
            else:
                self._chat.insert("end", f"{texto}\n", tag)
            self._chat.see("end")
            self._chat.configure(state="disabled")

        self.ventana.after(DELAY_MS, insertar)

    def _agregar_mensaje_con_efecto(self, texto: str, es_usuario: bool = False):
        if es_usuario:
            self._agregar_mensaje(texto, True)
            return
        self._mostrar_typing()
        threading.Thread(target=self._simular_escritura, args=(texto,), daemon=True).start()

    def _simular_escritura(self, texto: str):
        time.sleep(DELAY_MS / 1000)
        self.ventana.after(0, lambda: self._agregar_mensaje(texto, False))

    def _mostrar_typing(self):
        if self._typing_activo:
            return
        self._typing_activo = True

        def mostrar():
            self._chat.configure(state="normal")
            tag_start = self._chat.index("end-1c")
            self._chat.insert("end", "● ● ●\n", "typing")
            self._tag_typing_start = tag_start
            self._chat.see("end")
            self._chat.configure(state="disabled")
            self._animar_typing(0)

        self.ventana.after(0, mostrar)

    def _animar_typing(self, paso: int):
        if not self._typing_activo:
            return
        dots = ["● ● ●", "● ● ○", "● ○ ○", "○ ○ ○", "● ○ ○", "● ● ○"]
        def actualizar():
            try:
                self._chat.configure(state="normal")
                idx = paso % len(dots)
                texto = dots[idx]
                self._chat.delete("end-2l", "end-1l")
                self._chat.insert("end", texto + "\n", "typing")
                self._chat.see("end")
                self._chat.configure(state="disabled")
            except Exception:
                pass
        self.ventana.after(0, actualizar)
        if self._typing_activo:
            self.ventana.after(600, lambda: self._animar_typing(paso + 1))

    def _ocultar_typing(self):
        if not self._typing_activo:
            return
        self._typing_activo = False
        def ocultar():
            try:
                self._chat.configure(state="normal")
                self._chat.delete("end-2l", "end-1l")
                self._chat.see("end")
                self._chat.configure(state="disabled")
            except Exception:
                pass
        self.ventana.after(0, ocultar)

    def _limpiar_botones_opciones(self):
        for widget in self._botones_opciones_actuales:
            try:
                widget.destroy()
            except Exception:
                pass
        self._botones_opciones_actuales.clear()

    def _mostrar_botones_opciones(self, opciones: list[dict]):
        self._limpiar_botones_opciones()
        textos = {
            "físicos": "Físico", "fisicos": "Físico",
            "mentales": "Mental", "cognitivos": "Mental",
            "emocionales": "Emocional",
        }
        for i, opcion in enumerate(opciones):
            texto = opcion["texto"]
            marco = ctk.CTkButton(
                self._chat_frame,
                text=texto, cursor="hand2",
                command=lambda idx=i: self._on_boton_opcion(idx),
                fg_color=self._t["bubble_bot"],
                hover_color=self._t["border"],
                text_color=self._t["text"],
                corner_radius=14,
                height=44,
                font=("Segoe UI", 12),
                anchor="w",
            )
            marco.pack(fill="x", padx=14, pady=3)
            self._botones_opciones_actuales.append(marco)

    def _on_boton_opcion(self, indice: int):
        if self._procesando:
            return
        self._procesando = True
        self._limpiar_botones_opciones()
        threading.Thread(target=lambda: self._ejecutar_opcion(indice), daemon=True).start()

    def _iniciar_conversacion(self):
        mensaje = self.motor.obtener_pregunta()
        self._agregar_mensaje_con_efecto(mensaje)
        opciones = self.motor.obtener_opciones()
        if opciones:
            self.ventana.after(DELAY_MS + 200, lambda: self._mostrar_botones_opciones(opciones))

    def _ejecutar_opcion(self, indice: int):
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
        if hasattr(self, '_nodo_anterior') and self._nodo_anterior is not None:
            confirmacion = construir_mensaje_confirmacion(
                self._nodo_anterior, self.sesion, texto_opcion
            )
            self._agregar_mensaje_con_efecto(confirmacion)
        self._nodo_anterior = self.motor.obtener_nodo_actual()
        if self.motor.es_nodo_hoja():
            self._procesar_nodo_hoja()
        else:
            self._procesar_nodo_decision()
        self._procesando = False

    def _procesar_nodo_decision(self):
        mensaje = self.motor.obtener_pregunta()
        self._agregar_mensaje_con_efecto(mensaje)
        opciones = self.motor.obtener_opciones()
        if opciones:
            self.ventana.after(DELAY_MS + 200, lambda: self._mostrar_botones_opciones(opciones))

    def _procesar_nodo_hoja(self):
        diagnostico = self.motor.obtener_diagnostico()
        self._agregar_mensaje_con_efecto(diagnostico)
        self._ejecutar_spotify()

    def _ejecutar_spotify(self):
        nodo = self.motor.obtener_nodo_actual()
        if not nodo.get("spotify_query"):
            self._mostrar_boton_reiniciar()
            return
        threading.Thread(target=self._resolver_playlist_async, daemon=True).start()

    def _resolver_playlist_async(self):
        nodo = self.motor.obtener_nodo_actual()
        resultado = spotify.resolver_playlist(nodo)
        if resultado is None:
            msg = "No pude obtener la playlist en este momento. Intenta más tarde."
            self.ventana.after(0, lambda: self._agregar_mensaje(msg))
            self.ventana.after(0, self._mostrar_boton_reiniciar)
            return
        nombre = resultado.get("nombre", "Playlist recomendada")
        url = resultado.get("url", "")
        desc = resultado.get("descripcion", "")
        msg = f"Playlist: {nombre}\n{desc}\n\nEscúchala aquí: {url}"
        self.ventana.after(0, lambda: self._agregar_mensaje(msg))
        self._resultado_playlist = resultado
        self.ventana.after(1000, self._mostrar_acciones_playlist)

    def _mostrar_acciones_playlist(self):
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

        marco = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        marco.pack(fill="x", padx=10, pady=(4, 4))

        if url:
            btn = ctk.CTkButton(
                marco, text="Abrir en Spotify",
                command=abrir_spotify,
                fg_color="#1DB954", hover_color="#1AA34A",
                text_color="white", corner_radius=20, height=38,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(fill="x", padx=5, pady=3, side="top")
            self._botones_opciones_actuales.append(btn)

        if self.token_spotify:
            btn = ctk.CTkButton(
                marco, text="Reproducir ahora",
                command=reproducir,
                fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
                text_color="white", corner_radius=20, height=38,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(fill="x", padx=5, pady=3, side="top")
            self._botones_opciones_actuales.append(btn)

        btn = ctk.CTkButton(
            marco, text="Nuevo diagnóstico",
            command=nuevo,
            fg_color=self._t["border"], hover_color=self._t["text_sec"],
            text_color=self._t["text"], corner_radius=20, height=38,
            font=("Segoe UI", 12, "bold"),
        )
        btn.pack(fill="x", padx=5, pady=3, side="top")
        self._botones_opciones_actuales.append(btn)

    def _mostrar_boton_reiniciar(self):
        marco = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        marco.pack(fill="x", padx=10, pady=(4, 4))
        btn = ctk.CTkButton(
            marco, text="Nuevo diagnóstico",
            command=self._reiniciar_diagnostico,
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
            text_color="white", corner_radius=20, height=38,
            font=("Segoe UI", 12, "bold"),
        )
        btn.pack(fill="x", padx=5, pady=3)
        self._botones_opciones_actuales.append(btn)

    def _intentar_reproduccion(self, playlist: dict):
        try:
            sp = spotify.crear_cliente(self.token_spotify)
            uri = f"spotify:playlist:{playlist['id']}"
            res = spotify.reproducir_playlist(sp, uri)
            if res["resultado"] == "ok":
                self.ventana.after(0, lambda: self._agregar_mensaje("Reproduciendo 🎧"))
            elif res["resultado"] == "free_account":
                self._mostrar_sin_dispositivo(playlist, res["dispositivos"], free=True)
            else:
                self._mostrar_sin_dispositivo(playlist, res["dispositivos"])
        except Exception as e:
            logger.error(f"Error reproducción: {e}")

    def _mostrar_sin_dispositivo(self, playlist: dict, dispositivos: list[dict], free: bool = False):
        if free:
            msg = "Tu cuenta es Free. Abre Spotify y reproduce la playlist manualmente."
        elif not dispositivos:
            msg = "No detecté dispositivos. Abre Spotify en tu PC o celular, reproduce algo y presiona Reintentar."
        else:
            nombres = [d.get("name", "?") for d in dispositivos]
            msg = (
                f"Dispositivos: {', '.join(nombres)}.\n"
                "Reproduce algo en Spotify para activarlo, luego presiona Reintentar."
            )
        self.ventana.after(0, lambda: self._agregar_mensaje(msg))
        self._mostrar_boton_reintentar(playlist)

    def _mostrar_boton_reintentar(self, playlist: dict):
        def reintentar():
            self._intentar_reproduccion(playlist)
        marco = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        marco.pack(fill="x", padx=10, pady=(2, 4))
        btn = ctk.CTkButton(
            marco, text="Reintentar",
            command=reintentar,
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
            text_color="white", corner_radius=20, height=38,
            font=("Segoe UI", 12, "bold"),
        )
        btn.pack(fill="x", padx=5, pady=3)
        self._botones_opciones_actuales.append(btn)

    def _actualizar_btn_conectado(self, nombre: str):
        self._btn_spotify.configure(
            text=nombre,
            command=self._desvincular_spotify,
            fg_color="#1E6B38", hover_color=self._t["red"],
        )

    def _desvincular_spotify(self):
        self.token_spotify = None
        self._btn_spotify.configure(
            text="Spotify",
            command=self._iniciar_sesion_spotify,
            fg_color=self._t["green"], hover_color=self._t["accent_hover"],
            text_color="white",
        )
        for f in [".cache", ".spotify_cache.json"]:
            p = os.path.join(os.getcwd(), f)
            if os.path.exists(p):
                os.remove(p)
        self._agregar_mensaje("Spotify desconectado.")

    def _iniciar_sesion_spotify(self):
        global _callback_code, _callback_event
        _callback_code = None
        _callback_event.clear()
        try:
            servidor = HTTPServer((OAUTH_HOST, OAUTH_PORT), _DesktopOAuthHandler)
            hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
            hilo.start()
            oauth = spotify.crear_oauth()
            auth_url = oauth.get_authorize_url()
            webbrowser.open(auth_url)
            self._agregar_mensaje("Se abrió el navegador para autorizar Spotify.")
            threading.Thread(
                target=self._esperar_callback_oauth,
                args=(servidor, oauth), daemon=True,
            ).start()
        except OSError:
            self._agregar_mensaje("Puerto 8888 ocupado. Cierra otros procesos.")
        except Exception as e:
            logger.error(f"Error Spotify: {e}")
            self._agregar_mensaje("Error al iniciar sesión. Verifica tu .env")

    def _esperar_callback_oauth(self, servidor: HTTPServer, oauth: SpotifyOAuth):
        global _callback_code, _callback_event
        if _callback_event.wait(timeout=180):
            try:
                resultado = oauth.get_access_token(_callback_code, as_dict=True)
                self.token_spotify = resultado["access_token"] if isinstance(resultado, dict) else resultado
                nombre = "Spotify"
                try:
                    sp_temp = spotipy.Spotify(auth=self.token_spotify)
                    perfil = sp_temp.me()
                    nombre = perfil.get("display_name", "Spotify")
                    self._nombre_spotify = nombre
                except Exception:
                    pass
                self.ventana.after(0, lambda n=nombre: self._actualizar_btn_conectado(n))
            except Exception as e:
                logger.error(f"Token error: {e}")
                self.ventana.after(0, lambda: self._agregar_mensaje("Error al obtener token."))
        else:
            self.ventana.after(0, lambda: self._agregar_mensaje("Tiempo agotado."))
        servidor.shutdown()

    def _enviar_texto(self):
        if self._procesando:
            return
        texto = self._entry.get().strip()
        if not texto:
            return
        self._entry.delete(0, "end")
        self._agregar_mensaje(texto, es_usuario=True)
        self._agregar_mensaje_con_efecto(
            "No entendí del todo. Por favor, selecciona una opción de los botones."
        )

    def _reiniciar_diagnostico(self):
        self.motor.reiniciar()
        self._nodo_anterior = None
        self._procesando = False
        self._fallos_consecutivos = 0
        self._esperando_feedback = False
        self._limpiar_botones_opciones()
        if hasattr(self, '_resultado_playlist'):
            del self._resultado_playlist
        self._chat.configure(state="normal")
        self._chat.delete("1.0", "end")
        self._chat.configure(state="disabled")
        for attr in ["_tag_typing_start"]:
            if hasattr(self, attr):
                delattr(self, attr)
        self._typing_activo = False
        self._iniciar_conversacion()

    def ejecutar(self):
        self.ventana.mainloop()
