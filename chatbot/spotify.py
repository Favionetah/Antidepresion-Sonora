import logging
import time
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_MARKET
from .spotify_cache import obtener as cache_obtener, guardar as cache_guardar

logger = logging.getLogger(__name__)

_cache_playlists: dict[str, dict] = {}

PLAYLIST_MIN_TRACKS = 10
SEARCH_LIMIT = 10


def crear_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-read-playback-state user-modify-playback-state user-read-private",
        cache_path=None,
    )


def crear_cliente(token: Optional[str] = None) -> spotipy.Spotify:
    if token:
        return spotipy.Spotify(auth=token)
    oauth = crear_oauth()
    return spotipy.Spotify(auth_manager=oauth)


def resolver_playlist(nodo: dict) -> Optional[dict]:
    query = nodo.get("spotify_query", "").strip()
    if not query:
        return None

    if query in _cache_playlists:
        logger.info(f"Usando caché memoria para: {query}")
        resultado = dict(_cache_playlists[query])
        nodo["spotify_playlist_id"] = resultado["id"]
        nodo["spotify_playlist_url"] = resultado["url"]
        nodo["playlist_nombre"] = resultado["nombre"]
        nodo["playlist_descripcion"] = resultado["descripcion"]
        return resultado

    cache_disco = cache_obtener(query)
    if cache_disco:
        logger.info(f"Usando caché disco para: {query}")
        _cache_playlists[query] = cache_disco
        nodo["spotify_playlist_id"] = cache_disco["id"]
        nodo["spotify_playlist_url"] = cache_disco["url"]
        nodo["playlist_nombre"] = cache_disco["nombre"]
        nodo["playlist_descripcion"] = cache_disco["descripcion"]
        return cache_disco

    market = nodo.get("spotify_market") or SPOTIFY_MARKET

    for intento in range(2):
        try:
            sp = crear_cliente()
            respuesta = sp.search(
                q=query,
                type="playlist",
                limit=SEARCH_LIMIT,
                market=market,
            )
            playlists = respuesta.get("playlists", {}).get("items", [])
            playlists = [p for p in playlists if p is not None]
            if not playlists:
                logger.warning(f"Sin resultados para query: {query}")
                if intento == 0:
                    continue
                return None

            mejor = _seleccionar_mejor_playlist(playlists)
            if mejor is None:
                if intento == 0:
                    continue
                return None

            resultado = {
                "id": mejor["id"],
                "url": mejor.get("external_urls", {}).get("spotify", ""),
                "nombre": mejor.get("name", ""),
                "descripcion": mejor.get("description", "") or "",
            }

            _cache_playlists[query] = resultado
            cache_guardar(query, resultado)

            nodo["spotify_playlist_id"] = resultado["id"]
            nodo["spotify_playlist_url"] = resultado["url"]
            nodo["playlist_nombre"] = resultado["nombre"]
            nodo["playlist_descripcion"] = resultado["descripcion"]

            return resultado

        except spotipy.SpotifyException as e:
            logger.error(f"Error Spotify (intento {intento + 1}): {e}")
            if intento == 0:
                time.sleep(0.5)
                continue
            return None
        except Exception as e:
            logger.error(f"Error inesperado (intento {intento + 1}): {e}")
            if intento == 0:
                time.sleep(0.5)
                continue
            return None

    return None


def _seleccionar_mejor_playlist(playlists: list[dict]) -> Optional[dict]:
    if not playlists:
        return None

    for pl in playlists:
        try:
            nombre = (pl.get("name") or "").strip()
            desc = (pl.get("description") or "").strip()
            tracks = pl.get("tracks", {})
            total_tracks = tracks.get("total", 0) if isinstance(tracks, dict) else 0
            if nombre and total_tracks >= PLAYLIST_MIN_TRACKS:
                return pl
        except (KeyError, TypeError, AttributeError):
            continue

    for pl in playlists:
        try:
            tracks = pl.get("tracks", {})
            total_tracks = tracks.get("total", 0) if isinstance(tracks, dict) else 0
            if total_tracks >= 1:
                return pl
        except (KeyError, TypeError, AttributeError):
            continue

    return playlists[0] if playlists else None


def limpiar_cache() -> None:
    _cache_playlists.clear()


def obtener_dispositivos(sp: spotipy.Spotify) -> list[dict]:
    try:
        dispositivos = sp.devices()
        return dispositivos.get("devices", [])
    except Exception as e:
        logger.error(f"Error al obtener dispositivos: {e}")
        return []


def obtener_dispositivo_activo(sp: spotipy.Spotify) -> Optional[dict]:
    devices = obtener_dispositivos(sp)
    for d in devices:
        if d.get("is_active"):
            return d
    for d in devices:
        if d.get("type") in ("computer", "speaker", "phone"):
            return d
    return None


def verificar_cuenta_premium(sp: spotipy.Spotify) -> bool:
    try:
        perfil = sp.me()
        producto = perfil.get("product", "")
        return producto == "premium"
    except Exception as e:
        logger.error(f"Error al verificar cuenta: {e}")
        return False


def reproducir_playlist(sp: spotipy.Spotify, playlist_uri: str) -> dict:
    resultado = ""
    dispositivos_encontrados = obtener_dispositivos(sp)

    logger.info(f"Dispositivos disponibles: {len(dispositivos_encontrados)}")
    for d in dispositivos_encontrados:
        logger.info(f"  - {d.get('name')}: active={d.get('is_active')}, id={d.get('id')[:8]}...")

    try:
        sp.start_playback(context_uri=playlist_uri)
        return {"resultado": "ok", "dispositivos": dispositivos_encontrados}
    except spotipy.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e) or e.http_status == 404:
            resultado = "no_device"
        elif e.http_status == 403:
            resultado = "free_account"
        else:
            logger.error(f"Error al reproducir: {e}")
            resultado = "error"
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        resultado = "error"

    if resultado in ("no_device", "error") and dispositivos_encontrados:
        for dispositivo in dispositivos_encontrados:
            did = dispositivo.get("id", "")
            if not did:
                continue
            try:
                sp.start_playback(device_id=did, context_uri=playlist_uri)
                logger.info(f"Reproduciendo en: {dispositivo.get('name')}")
                return {"resultado": "ok", "dispositivos": dispositivos_encontrados}
            except spotipy.SpotifyException as e:
                if e.http_status == 403:
                    resultado = "free_account"
                logger.warning(f"Fallo en {dispositivo.get('name')}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error inesperado en {dispositivo.get('name')}: {e}")
                continue

    return {"resultado": resultado, "dispositivos": dispositivos_encontrados}


def obtener_canciones_playlist(sp: spotipy.Spotify, playlist_id: str, limit: int = 10) -> list[dict]:
    try:
        resultados = sp.playlist_tracks(playlist_id, limit=limit)
        canciones = []
        for item in resultados.get("items", []):
            track = item.get("track")
            if track is None:
                continue
            nombre = track.get("name", "Sin nombre")
            artista = ", ".join(
                a.get("name", "") for a in track.get("artists", []) if a
            )
            url = track.get("external_urls", {}).get("spotify", "")
            canciones.append({"nombre": nombre, "artista": artista, "url": url})
        return canciones
    except Exception as e:
        logger.error(f"Error al obtener canciones: {e}")
        return []
