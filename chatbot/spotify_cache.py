import json
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".spotify_cache.json")
CACHE_TTL = 86400 * 7


def _cargar_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        ahora = time.time()
        return {k: v for k, v in data.items() if v.get("_ts", 0) + CACHE_TTL > ahora}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Error al leer caché: {e}")
        return {}


def _guardar_cache(cache: dict) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.warning(f"Error al escribir caché: {e}")


def obtener(query: str) -> Optional[dict]:
    cache = _cargar_cache()
    entry = cache.get(query)
    if entry:
        logger.info(f"Cache hit: {query}")
        return {k: v for k, v in entry.items() if k != "_ts"}
    return None


def guardar(query: str, resultado: dict) -> None:
    cache = _cargar_cache()
    entry = dict(resultado)
    entry["_ts"] = time.time()
    cache[query] = entry
    _guardar_cache(cache)


def limpiar() -> None:
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except OSError:
            pass
