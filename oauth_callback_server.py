import logging
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

import spotipy

from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
from telegram_bot import SESIONES

logger = logging.getLogger(__name__)


class OAuthCallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        try:
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            code = params.get("code", [None])[0]
            state = params.get("state", [None])[0]

            if not code or not state:
                self._responder_error()
                return

            try:
                chat_id = int(state)
            except (ValueError, TypeError):
                logger.error(f"State inválido: {state}")
                self._responder_error()
                return

            oauth = spotipy.oauth2.SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                scope="user-read-playback-state user-modify-playback-state",
                cache_path=None,
            )

            token_info = oauth.get_access_token(code, as_dict=False)
            if not token_info:
                logger.error("No se pudo obtener el token de acceso")
                self._responder_error()
                return

            if chat_id in SESIONES:
                SESIONES[chat_id].token_spotify = token_info["access_token"]
                logger.info(f"Token de Spotify almacenado para chat_id {chat_id}")
            else:
                logger.warning(f"Sesión no encontrada para chat_id {chat_id}")

            self._responder_exito()

        except Exception as e:
            logger.error(f"Error en callback OAuth: {e}\n{traceback.format_exc()}")
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
            "<p>Ya puedes volver a Telegram y continuar.</p>"
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
            "<p>Intenta de nuevo desde Telegram con el comando /spotify.</p>"
            "</div></body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args) -> None:
        logger.info(f"OAuth Server: {format % args}")


def iniciar_servidor_oauth(host: str = "localhost", port: int = 8888) -> None:
    try:
        servidor = HTTPServer((host, port), OAuthCallbackHandler)
        logger.info(f"Servidor OAuth escuchando en http://{host}:{port}/callback")
        servidor.serve_forever()
    except OSError as e:
        logger.error(f"No se pudo iniciar servidor OAuth en {host}:{port}: {e}")
    except Exception as e:
        logger.error(f"Error en servidor OAuth: {e}")
