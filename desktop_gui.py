import io
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
from PIL import Image, ImageDraw, ImageFilter
from spotipy.oauth2 import SpotifyOAuth

from chatbot import MotorFSM, SesionSBC
from chatbot import spotify
from chatbot.frases import (
    construir_mensaje_confirmacion,
    construir_mensaje_diagnostico,
)

logger = logging.getLogger(__name__)

LIGHT = {
    "bg": "#F5F0EB",
    "card": "#FFFFFF",
    "primary": "#D4933A",
    "primary_hover": "#B87D2E",
    "accent": "#8B6F47",
    "accent_hover": "#7A5F3A",
    "text": "#1D1D1F",
    "text_sec": "#86868B",
    "border": "#E5E0D8",
    "red": "#E05A5A",
    "red_hover": "#CC4444",
    "chat": "#FAF8F5",
    "bubble_bot": "#FFFFFF",
    "bubble_user": "#D4933A",
    "bubble_user_text": "#FFFFFF",
    "bubble_bot_text": "#1D1D1F",
    "input_bg": "#FFFFFF",
    "input_border": "#E5E0D8",
    "green": "#1DB954",
    "amber": "#D4933A",
    "player_bg": "#1A1A1A",
    "player_text": "#FFFFFF",
    "player_sec": "#A0A0A0",
    "gold": "#D4933A",
}

DARK = {
    "bg": "#1C1C1E",
    "card": "#2C2C2E",
    "primary": "#D4933A",
    "primary_hover": "#B87D2E",
    "accent": "#A88B6F",
    "accent_hover": "#967A60",
    "text": "#F5F5F7",
    "text_sec": "#98989D",
    "border": "#38383A",
    "red": "#E05A5A",
    "red_hover": "#CC4444",
    "chat": "#222224",
    "bubble_bot": "#2C2C2E",
    "bubble_user": "#D4933A",
    "bubble_user_text": "#FFFFFF",
    "bubble_bot_text": "#F5F5F7",
    "input_bg": "#2C2C2E",
    "input_border": "#38383A",
    "green": "#1DB954",
    "amber": "#D4933A",
    "player_bg": "#0A0A0A",
    "player_text": "#FFFFFF",
    "player_sec": "#8E8E93",
    "gold": "#D4933A",
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
        w, h = 420, 340
        self.geometry(f"{w}x{h}+{parent.winfo_screenwidth() // 2 - w // 2}+{parent.winfo_screenheight() // 2 - h // 2}")
        self.configure(fg_color=self._theme["bg"])
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        bg_img = self._crear_fondo_gradiente(w, h)
        bg_label = ctk.CTkLabel(self, text="", image=bg_img)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = os.path.join(RUTA_ICONOS, "splash_logo.png")
        if os.path.exists(logo_path):
            pil = Image.open(logo_path).resize((64, 64), Image.LANCZOS)
            ctk_img = ctk.CTkImage(pil, size=(64, 64))
            lbl_logo = ctk.CTkLabel(marco, image=ctk_img, text="")
            lbl_logo.pack(pady=(20, 0))

        ctk.CTkLabel(
            marco,
            text="Antidepresión Sonora",
            font=("Raleway", 24, "bold"),
            text_color=self._theme["text"],
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            marco,
            text="Musicoterapia personalizada",
            font=("Segoe UI", 11),
            text_color=self._theme["text_sec"],
        ).pack(pady=(0, 28))

        barra_frame = ctk.CTkFrame(self, fg_color="transparent", width=240, height=3)
        barra_frame.place(relx=0.5, rely=0.72, anchor="center")

        self._barra = ctk.CTkProgressBar(
            barra_frame, width=240, height=3,
            fg_color=self._theme["border"],
            progress_color=self._theme["primary"],
            corner_radius=1,
        )
        self._barra.pack()
        self._barra.set(0)

        ctk.CTkLabel(
            self,
            text="Preparando tu experiencia...",
            font=("Segoe UI", 10),
            text_color=self._theme["text_sec"],
        ).place(relx=0.5, rely=0.78, anchor="center")

        self._animar_barra()
        self.after(1800, self.destroy)

    def _crear_fondo_gradiente(self, w: int, h: int) -> ctk.CTkImage:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bg = self._theme["bg"]
        card = self._theme["card"]
        from_color = Image.new("RGBA", (w, h), bg)
        to_color = Image.new("RGBA", (w, h), card)
        grad = Image.blend(from_color, to_color, 0.15)
        draw = ImageDraw.Draw(grad)
        cx, cy, r = w // 2, h // 2 - 20, 160
        for i in range(100):
            alpha = max(0, 8 - i // 12)
            if alpha <= 0:
                break
            r2 = int(r * (1 - i / 120))
            draw.ellipse(
                [(cx - r2, cy - r2), (cx + r2, cy + r2)],
                outline=(212, 147, 58, alpha),
                width=1,
            )
        ctk_img = ctk.CTkImage(grad, size=(w, h))
        return ctk_img

    def _animar_barra(self):
        def animar(paso=0):
            if paso > 100:
                self.after(200, self._fade_out)
                return
            self._barra.set(paso / 100)
            self.after(16, lambda: animar(paso + 2))
        animar()

    def _fade_out(self):
        self.destroy()


def _cargar_icono(nombre: str, size: int = 22) -> Optional[ctk.CTkImage]:
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
        self._player_visible = False
        self._player_reproduciendo = False
        self._player_volumen = 80
        self._player_shuffle = False
        self._player_repeat = "off"
        self._player_progreso_ms = 0
        self._player_duracion_ms = 0
        self._player_cancion = ""
        self._player_artista = ""
        self._player_album_art_bytes: Optional[bytes] = None
        self._polling_activo = False
        self._sp_cliente: Optional[spotipy.Spotify] = None
        self._album_art_cache: dict[str, bytes] = {}
        self._after_ids: list[int] = []
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
        for nombre in ("spotify", "send", "retry", "disconnect", "new", "check", "moon", "sun",
                        "play", "pause", "prev", "next", "volume", "shuffle", "repeat"):
            icono = _cargar_icono(nombre)
            if icono:
                self._iconos[nombre] = icono

    def _aplicar_tema(self):
        self._t = dict(DARK if self._dark else LIGHT)
        modo = "dark" if self._dark else "light"
        ctk.set_appearance_mode(modo)

        self.ventana.configure(fg_color=self._t["bg"])
        self._barra_sup.configure(fg_color=self._t["card"], border_color=self._t["border"])
        if hasattr(self, '_shadow_frame'):
            self._shadow_frame.configure(fg_color=self._t["border"])
        self._chat_frame.configure(fg_color=self._t["card"])
        self._chat.configure(fg_color=self._t["chat"], text_color=self._t["text"])
        self._chat.tag_config("bubble_bot", foreground=self._t["bubble_bot_text"])
        self._chat.tag_config("bubble_bot_gold", foreground=self._t["gold"])
        self._chat.tag_config("bubble_user", foreground=self._t["bubble_user_text"])
        self._chat.tag_config("typing", foreground=self._t["text_sec"])
        self._chat.tag_config("diagnostico", foreground=self._t["bubble_bot_text"])
        self._chat.tag_config("separador", foreground=self._t["border"])
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

        self._logo_icono.configure(text_color=self._t["primary"])
        self._logo_titulo.configure(text_color=self._t["text"])
        self._logo_sub.configure(text_color=self._t["text_sec"])

        if self.token_spotify:
            self._actualizar_btn_conectado(self._nombre_spotify if hasattr(self, '_nombre_spotify') else "Spotify")

        self._btn_tema.configure(
            image=self._iconos.get("sun" if self._dark else "moon"),
            fg_color=self._t["card"], hover_color=self._t["border"],
        )

        if hasattr(self, '_player_frame'):
            self._player_frame.configure(fg_color=self._t["player_bg"])
            self._player_cancion_label.configure(text_color=self._t["player_text"])
            self._player_artista_label.configure(text_color=self._t["player_sec"])
            self._player_progresso.configure(
                fg_color=self._t["player_sec"], progress_color=self._t["gold"],
            )

        for btn in self._botones_opciones_actuales:
            try:
                texto = btn.cget("text")
                if "Nuevo" in texto:
                    btn.configure(text_color=self._t["text_sec"], border_color=self._t["border"])
                elif "Abrir" in texto:
                    btn.configure(fg_color="#1DB954", text_color="white")
                elif "Reproducir" in texto or "Reintentar" in texto:
                    btn.configure(fg_color=self._t["primary"], text_color="white", hover_color=self._t["primary_hover"])
                else:
                    btn.configure(fg_color=self._t["bubble_bot"], text_color=self._t["text"],
                                  border_color=self._t["border"], hover_color=self._t["border"])
            except Exception:
                pass

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

        logo_frame = ctk.CTkFrame(marco, fg_color="transparent")
        logo_frame.pack(side="left")

        self._logo_icono = ctk.CTkLabel(
            logo_frame, text="♪", font=("Segoe UI", 18),
            text_color=self._t["primary"],
        )
        self._logo_icono.pack(side="left", padx=(0, 8))

        self._logo_titulo = ctk.CTkLabel(
            logo_frame, text="Antidepresión Sonora",
            font=("Raleway", 16, "bold"), text_color=self._t["text"],
        )
        self._logo_titulo.pack(side="left")

        self._logo_sub = ctk.CTkLabel(
            logo_frame, text="Musicoterapia",
            font=("Segoe UI", 9), text_color=self._t["text_sec"],
        )
        self._logo_sub.pack(side="left", padx=(8, 0), pady=(4, 0))

        self._btn_reiniciar = ctk.CTkButton(
            marco, text="Nuevo", width=72, height=34,
            command=self._reiniciar_diagnostico,
            fg_color="transparent", hover_color=self._t["border"],
            text_color=self._t["text"], corner_radius=17,
            border_width=1, border_color=self._t["border"],
            font=("Segoe UI", 11),
        )
        self._btn_reiniciar.pack(side="right", padx=(0, 0))

        self._btn_spotify = ctk.CTkButton(
            marco, text="Spotify", width=80, height=34,
            command=self._iniciar_sesion_spotify,
            fg_color=self._t["green"], hover_color="#1AA34A",
            text_color="white", corner_radius=17, font=("Segoe UI", 11, "bold"),
        )
        self._btn_spotify.pack(side="right", padx=(6, 6))

        self._btn_tema = ctk.CTkButton(
            marco, text="", width=34, height=34,
            image=self._iconos.get("moon"),
            command=self._toggle_tema,
            fg_color="transparent", hover_color=self._t["border"],
            corner_radius=17,
        )
        self._btn_tema.pack(side="right", padx=(0, 0))

    def _construir_chat(self):
        self._shadow_frame = ctk.CTkFrame(
            self.ventana, fg_color=self._t["border"],
            corner_radius=16,
        )
        self._shadow_frame.pack(fill="both", expand=True, padx=14, pady=(10, 6))
        self._shadow_frame.pack_propagate(False)

        self._chat_frame = ctk.CTkFrame(
            self._shadow_frame, fg_color=self._t["card"],
            corner_radius=16, border_width=0,
        )
        self._chat_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self._chat = ctk.CTkTextbox(
            self._chat_frame,
            wrap="word", state="disabled",
            fg_color=self._t["chat"], text_color=self._t["text"],
            font=("Segoe UI", 13),
            corner_radius=12, border_width=0,
            scrollbar_button_color=self._t["primary"],
            scrollbar_button_hover_color=self._t["primary_hover"],
        )
        self._chat.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        self._chat.tag_config("bubble_bot", lmargin1=16, lmargin2=12, rmargin=72,
                              foreground=self._t["bubble_bot_text"],
                              spacing1=5, spacing3=5)

        self._chat.tag_config("bubble_bot_gold", lmargin1=16, lmargin2=12, rmargin=72,
                              foreground=self._t["gold"],
                              spacing1=2, spacing3=4)

        self._chat.tag_config("bubble_user", lmargin1=72, lmargin2=68, rmargin=16,
                              foreground=self._t["bubble_user_text"],
                              spacing1=5, spacing3=5, justify="right")

        self._chat.tag_config("typing", lmargin1=16, rmargin=72,
                              foreground=self._t["text_sec"], spacing1=2, spacing3=2)

        self._chat.tag_config("diagnostico", lmargin1=16, lmargin2=12, rmargin=72,
                              foreground=self._t["bubble_bot_text"],
                              spacing1=5, spacing3=8)

        self._chat.tag_config("separador", lmargin1=16, rmargin=16,
                              foreground=self._t["border"],
                              spacing1=4, spacing3=4)

        self._construir_player()

    def _construir_input(self):
        contenedor = ctk.CTkFrame(self.ventana, fg_color="transparent", height=52)
        contenedor.pack(fill="x", padx=14, pady=(0, 14))
        contenedor.pack_propagate(False)

        self._input_frame = ctk.CTkFrame(
            contenedor, fg_color=self._t["card"],
            corner_radius=26, border_width=1, border_color=self._t["input_border"],
        )
        self._input_frame.pack(fill="both", expand=True)

        self._entry = ctk.CTkEntry(
            self._input_frame,
            placeholder_text="Describe cómo te sientes...",
            font=("Segoe UI", 13),
            fg_color="transparent", text_color=self._t["text"],
            border_width=0, corner_radius=26, height=34,
            placeholder_text_color=self._t["text_sec"],
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(16, 4), pady=7)
        self._entry.bind("<Return>", lambda e: self._enviar_texto())

        self._btn_enviar = ctk.CTkButton(
            self._input_frame, text="", width=34, height=34,
            image=self._iconos.get("send"),
            command=self._enviar_texto,
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
            corner_radius=17,
        )
        self._btn_enviar.pack(side="right", padx=(0, 5), pady=5)

    def _construir_player(self):
        self._player_frame = ctk.CTkFrame(
            self._chat_frame, fg_color=self._t["player_bg"],
            corner_radius=14, height=88,
        )
        self._player_frame.pack(fill="x", padx=8, pady=(6, 8))
        self._player_frame.pack_propagate(False)

        inner = ctk.CTkFrame(self._player_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, pady=(6, 0))

        self._album_art_label = ctk.CTkLabel(
            inner, text="", width=52, height=52,
            corner_radius=8, fg_color=self._t["player_sec"],
        )
        self._album_art_label.pack(side="left", padx=(10, 8), pady=4)

        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=4)

        self._player_cancion_label = ctk.CTkLabel(
            info_frame, text="Playlist lista",
            font=("Segoe UI", 12, "bold"),
            text_color=self._t["player_text"], anchor="w",
        )
        self._player_cancion_label.pack(fill="x", padx=(0, 4))

        self._player_artista_label = ctk.CTkLabel(
            info_frame, text="Presiona ▶ para reproducir",
            font=("Segoe UI", 10),
            text_color=self._t["player_sec"], anchor="w",
        )
        self._player_artista_label.pack(fill="x", padx=(0, 4))

        self._player_progresso = ctk.CTkProgressBar(
            info_frame, height=2,
            fg_color=self._t["player_sec"],
            progress_color=self._t["gold"],
            corner_radius=1,
        )
        self._player_progresso.pack(fill="x", padx=(0, 4), pady=(4, 0))
        self._player_progresso.set(0)

        control_frame = ctk.CTkFrame(inner, fg_color="transparent")
        control_frame.pack(side="right", padx=(0, 8), pady=4)

        self._btn_prev = ctk.CTkButton(
            control_frame, text="", width=30, height=30,
            image=self._iconos.get("prev"),
            command=self._player_anterior,
            fg_color="transparent", hover_color=self._t["player_sec"],
            corner_radius=15,
        )
        self._btn_prev.pack(side="left", padx=1)

        self._btn_play = ctk.CTkButton(
            control_frame, text="", width=36, height=36,
            image=self._iconos.get("play"),
            command=self._player_toggle,
            fg_color=self._t["gold"], hover_color=self._t["primary_hover"],
            corner_radius=18,
        )
        self._btn_play.pack(side="left", padx=1)

        self._btn_next = ctk.CTkButton(
            control_frame, text="", width=30, height=30,
            image=self._iconos.get("next"),
            command=self._player_siguiente,
            fg_color="transparent", hover_color=self._t["player_sec"],
            corner_radius=15,
        )
        self._btn_next.pack(side="left", padx=1)

        self._player_frame.pack_forget()
        self._player_visible = False

    def _mostrar_player(self):
        if self._player_visible:
            return
        self._player_visible = True
        self._player_frame.pack(fill="x", padx=8, pady=(6, 8))
        self._iniciar_polling()

    def _ocultar_player(self):
        self._player_visible = False
        self._detener_polling()
        self._player_frame.pack_forget()

    def _player_toggle(self):
        if not self._sp_cliente:
            return
        threading.Thread(target=self._player_toggle_async, daemon=True).start()

    def _player_toggle_async(self):
        if self._player_reproduciendo:
            resultado = spotify.pausar(self._sp_cliente)
        else:
            resultado = spotify.reanudar(self._sp_cliente)
        if resultado == "ok":
            self._player_reproduciendo = not self._player_reproduciendo
            self.ventana.after(0, self._actualizar_boton_play)

    def _player_anterior(self):
        if self._sp_cliente:
            threading.Thread(
                target=lambda: spotify.anterior(self._sp_cliente), daemon=True
            ).start()

    def _player_siguiente(self):
        if self._sp_cliente:
            threading.Thread(
                target=lambda: spotify.siguiente(self._sp_cliente), daemon=True
            ).start()

    def _player_reproducir_playlist(self):
        if not self._sp_cliente or not hasattr(self, '_resultado_playlist'):
            return
        playlist = self._resultado_playlist
        uri = f"spotify:playlist:{playlist['id']}"
        res = spotify.reproducir_playlist(self._sp_cliente, uri)
        if res.get("resultado") == "ok":
            self._player_reproduciendo = True
            self.ventana.after(0, self._actualizar_boton_play)

    def _player_forzar_actualizacion(self):
        if not self._sp_cliente:
            return
        try:
            estado = spotify.obtener_estado(self._sp_cliente)
            self._actualizar_player_ui(estado)
        except Exception as e:
            logger.debug(f"Forzar actualización: {e}")

    def _actualizar_boton_play(self):
        icono = "pause" if self._player_reproduciendo else "play"
        self._btn_play.configure(image=self._iconos.get(icono))

    def _actualizar_player_ui(self, estado: dict):
        if not estado.get("activo"):
            self._player_reproduciendo = False
            self._actualizar_boton_play()
            return
        self._player_reproduciendo = estado.get("reproduciendo", False)
        self._player_progreso_ms = estado.get("progreso_ms", 0)
        self._player_duracion_ms = estado.get("duracion_ms", 0)
        self._player_cancion = estado.get("cancion", "")
        self._player_artista = estado.get("artista", "")
        self._player_volumen = estado.get("volumen", 80)
        self._player_shuffle = estado.get("shuffle", False)
        self._player_repeat = estado.get("repeat", "off")

        self._player_cancion_label.configure(text=self._player_cancion or "Sin título")
        self._player_artista_label.configure(text=self._player_artista or "Artista desconocido")

        if self._player_duracion_ms > 0:
            progreso_ratio = self._player_progreso_ms / self._player_duracion_ms
            self._player_progresso.set(max(0, min(1, progreso_ratio)))

        album_art_url = estado.get("album_art", "")
        if album_art_url and album_art_url not in self._album_art_cache:
            datos = spotify.obtener_album_art(self._sp_cliente, album_art_url)
            if datos:
                self._album_art_cache[album_art_url] = datos
        if album_art_url in self._album_art_cache:
            datos = self._album_art_cache[album_art_url]
            img = Image.open(io.BytesIO(datos)).resize((52, 52), Image.LANCZOS)
            mask = Image.new("L", (52, 52), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, 52, 52), radius=6, fill=255)
            img.putalpha(mask)
            ctk_img = ctk.CTkImage(img, size=(52, 52))
            self._album_art_label.configure(image=ctk_img, text="")
        elif not album_art_url:
            self._album_art_label.configure(image="", text="♫",
                                            text_color=self._t["player_sec"],
                                            font=("Segoe UI", 20))

        self._actualizar_boton_play()

    def _iniciar_polling(self):
        if self._polling_activo or not self._sp_cliente:
            return
        self._polling_activo = True
        threading.Thread(target=self._polling_loop, daemon=True).start()

    def _detener_polling(self):
        self._polling_activo = False

    def _polling_loop(self):
        while self._polling_activo and self._sp_cliente:
            try:
                estado = spotify.obtener_estado(self._sp_cliente)
                self.ventana.after(0, lambda e=estado: self._actualizar_player_ui(e))
            except Exception as e:
                logger.debug(f"Polling error: {e}")
            for _ in range(30):
                if not self._polling_activo:
                    return
                time.sleep(0.1)

    def _agregar_mensaje(self, texto: str, es_usuario: bool = False, tag: str = ""):
        if self._typing_activo:
            self._ocultar_typing()

        def insertar():
            self._chat.configure(state="normal")
            t = tag or ("bubble_user" if es_usuario else "bubble_bot")
            self._chat.insert("end", f"{texto}\n", t)
            self._chat.see("end")
            self._chat.configure(state="disabled")

        self.ventana.after(DELAY_MS, insertar)

    def _agregar_mensaje_con_efecto(self, texto: str, es_usuario: bool = False, tag: str = ""):
        if es_usuario:
            self._agregar_mensaje(texto, True, tag=tag)
            return
        self._mostrar_typing()
        threading.Thread(target=self._simular_escritura, args=(texto, tag), daemon=True).start()

    def _simular_escritura(self, texto: str, tag: str = ""):
        time.sleep(DELAY_MS / 1000)
        self.ventana.after(0, lambda: self._agregar_mensaje(texto, False, tag=tag))

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
        frames = ["● ○ ○", "● ● ○", "● ● ●", "● ● ○", "● ○ ○", "○ ○ ○"]
        def actualizar():
            try:
                self._chat.configure(state="normal")
                idx = paso % len(frames)
                self._chat.delete("end-2l", "end-1l")
                self._chat.insert("end", frames[idx] + "\n", "typing")
                self._chat.see("end")
                self._chat.configure(state="disabled")
            except Exception:
                pass
        self.ventana.after(0, actualizar)
        if self._typing_activo:
            self.ventana.after(400, lambda: self._animar_typing(paso + 1))

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
        for i, opcion in enumerate(opciones):
            texto = opcion["texto"]
            marco = ctk.CTkButton(
                self._chat_frame,
                text=texto, cursor="hand2",
                command=lambda idx=i: self._on_boton_opcion(idx),
                fg_color=self._t["bubble_bot"],
                hover_color=self._t["border"],
                text_color=self._t["text"],
                corner_radius=12,
                height=42,
                font=("Segoe UI", 12),
                anchor="w",
                border_width=1, border_color=self._t["border"],
            )
            marco.pack(fill="x", padx=14, pady=2)
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
        self._agregar_mensaje("─── ⋆⋅☆⋅⋆ ───", tag="separador")
        self._agregar_mensaje_con_efecto(diagnostico, tag="diagnostico")
        self._agregar_mensaje("─── ⋆⋅☆⋅⋆ ───", tag="separador")
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
        self.ventana.after(0, lambda: self._agregar_mensaje(nombre, tag="bubble_bot_gold"))
        if desc:
            self.ventana.after(0, lambda d=desc: self._agregar_mensaje(d))
        self.ventana.after(0, lambda u=url: self._agregar_mensaje(u))
        self._resultado_playlist = resultado
        self._after(1000, self._mostrar_acciones_playlist)
        self._after(1500, self._mostrar_player)
        if self._sp_cliente:
            self._after(2000, self._player_reproducir_playlist)

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

        if url:
            btn = ctk.CTkButton(
                self._chat_frame, text="Abrir en Spotify",
                command=abrir_spotify,
                fg_color="#1DB954", hover_color="#1AA34A",
                text_color="white", corner_radius=16, height=38,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self._botones_opciones_actuales.append(btn)

        if self.token_spotify:
            btn = ctk.CTkButton(
                self._chat_frame, text="Reproducir ahora",
                command=reproducir,
                fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
                text_color="white", corner_radius=16, height=38,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self._botones_opciones_actuales.append(btn)

        btn = ctk.CTkButton(
            self._chat_frame, text="Nuevo diagnóstico",
            command=nuevo,
            fg_color="transparent", hover_color=self._t["border"],
            text_color=self._t["text_sec"], corner_radius=16, height=38,
            font=("Segoe UI", 12),
            border_width=1, border_color=self._t["border"],
        )
        btn.pack(fill="x", padx=14, pady=2)
        self._botones_opciones_actuales.append(btn)

    def _mostrar_boton_reiniciar(self):
        btn = ctk.CTkButton(
            self._chat_frame, text="Nuevo diagnóstico",
            command=self._reiniciar_diagnostico,
            fg_color="transparent", hover_color=self._t["border"],
            text_color=self._t["text_sec"], corner_radius=16, height=38,
            font=("Segoe UI", 12),
            border_width=1, border_color=self._t["border"],
        )
        btn.pack(fill="x", padx=14, pady=2)
        self._botones_opciones_actuales.append(btn)

    def _intentar_reproduccion(self, playlist: dict):
        try:
            sp = self._sp_cliente or spotify.crear_cliente(self.token_spotify)
            if not self._sp_cliente:
                self._sp_cliente = sp
            uri = f"spotify:playlist:{playlist['id']}"
            res = spotify.reproducir_playlist(sp, uri)
            if res["resultado"] == "ok":
                self._player_reproduciendo = True
                self.ventana.after(0, self._actualizar_boton_play)
                self._mostrar_player()
                self._iniciar_polling()
                self._after(500, self._player_forzar_actualizacion)
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
        btn = ctk.CTkButton(
            self._chat_frame, text="Reintentar",
            command=reintentar,
            fg_color=self._t["primary"], hover_color=self._t["primary_hover"],
            text_color="white", corner_radius=16, height=38,
            font=("Segoe UI", 12, "bold"),
        )
        btn.pack(fill="x", padx=14, pady=2)
        self._botones_opciones_actuales.append(btn)

    def _actualizar_btn_conectado(self, nombre: str):
        self._btn_spotify.configure(
            text=nombre,
            command=self._desvincular_spotify,
            fg_color="#1E6B38", hover_color=self._t["red"],
        )

    def _desvincular_spotify(self):
        self.token_spotify = None
        self._sp_cliente = None
        self._detener_polling()
        self._btn_spotify.configure(
            text="Spotify",
            command=self._iniciar_sesion_spotify,
            fg_color=self._t["green"], hover_color="#1AA34A",
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
                self._sp_cliente = spotipy.Spotify(auth=self.token_spotify)
                nombre = "Spotify"
                try:
                    perfil = self._sp_cliente.me()
                    nombre = perfil.get("display_name", "Spotify")
                    self._nombre_spotify = nombre
                except Exception:
                    pass
                self.ventana.after(0, lambda n=nombre: self._actualizar_btn_conectado(n))
                if self._player_visible:
                    self._iniciar_polling()
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
        self._procesando = True
        threading.Thread(target=self._procesar_texto_usuario, args=(texto,), daemon=True).start()

    def _procesar_texto_usuario(self, texto: str):
        try:
            resultado = self.motor.procesar_texto(texto)
            if resultado["tipo"] == "opcion":
                indice = resultado["indice"]
                opcion = self.motor.obtener_info_opcion(indice)
                if opcion:
                    destino = self.motor.transicionar(indice)
                    if not destino:
                        return
                    if hasattr(self, '_nodo_anterior') and self._nodo_anterior is not None:
                        confirmacion = construir_mensaje_confirmacion(
                            self._nodo_anterior, self.sesion, opcion["texto"]
                        )
                        self._agregar_mensaje_con_efecto(confirmacion)
                    self._nodo_anterior = self.motor.obtener_nodo_actual()
                    if self.motor.es_nodo_hoja():
                        self._procesar_nodo_hoja()
                    else:
                        self._procesar_nodo_decision()
            elif resultado["tipo"] == "redireccion":
                msg = self.motor.obtener_mensaje_empatico()
                if not msg:
                    msg = "Parece que tu estado emocional ha cambiado."
                self._agregar_mensaje_con_efecto(msg)
                opciones = self.motor.obtener_opciones()
                destinos = resultado["sugerencia"].get("destinos", [])
                opciones_filtradas = [o for o in opciones if o.get("destino", "") in destinos]
                if opciones_filtradas:
                    self.ventana.after(DELAY_MS + 200, lambda: self._mostrar_botones_opciones(opciones_filtradas))
            else:
                msg = self.motor.obtener_mensaje_empatico()
                if msg:
                    self._agregar_mensaje_con_efecto(msg)
                else:
                    self._agregar_mensaje_con_efecto(
                        "No entendí del todo. Por favor, selecciona una opción de los botones."
                    )
        except Exception as e:
            logger.error(f"Error procesando texto: {e}")
            self.ventana.after(0, lambda: self._agregar_mensaje_con_efecto(
                "Ocurrió un error. Selecciona una opción de los botones."
            ))
        finally:
            self._procesando = False

    def _cancelar_after_pendientes(self):
        for aid in self._after_ids:
            try:
                self.ventana.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def _after(self, ms: int, callback) -> int:
        aid = self.ventana.after(ms, callback)
        self._after_ids.append(aid)
        return aid

    def _reiniciar_diagnostico(self):
        self._cancelar_after_pendientes()
        self._detener_polling()
        self.motor.reiniciar()
        self._nodo_anterior = None
        self._procesando = False
        self._fallos_consecutivos = 0
        self._esperando_feedback = False
        self._limpiar_botones_opciones()
        if hasattr(self, '_resultado_playlist'):
            del self._resultado_playlist
        self._ocultar_player()
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
