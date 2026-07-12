import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
SPOTIFY_MARKET = os.getenv("SPOTIFY_MARKET", "MX")
OAUTH_HOST = os.getenv("OAUTH_HOST", "localhost")
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8888"))
