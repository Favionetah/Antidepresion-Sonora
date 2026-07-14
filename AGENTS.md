# AGENTS.md — Antidepresión Sonora (SBC Musicoterapia)

## Stack & Entrypoints

- **Desktop GUI**: `desktop_main.py` → `desktop_gui.py:ChatbotSBCApp`
- **Telegram bot**: `telegram_main.py` → `telegram_bot.py` handlers
- **Core package**: `chatbot/` (shared by both frontends)

## Run commands

```powershell
# Desktop (use venv — MSYS2 Python has no pip)
.\venv\bin\python.exe desktop_main.py

# Telegram bot
.\venv\bin\python.exe telegram_main.py

# Install deps
.\venv\bin\python.exe -m pip install -r requirements.txt

# Build .exe
pip install pyinstaller
pyinstaller --onefile --windowed desktop_main.py
```

## Core architecture (`chatbot/`)

| File | Role |
|------|------|
| `base_conocimiento.py` | 25-node decision tree (Singleton) |
| `motor_fsm.py` | Per-session FSM — `procesar_texto()` is the main entry |
| `contexto.py` | `SesionSBC` dataclass (nodo, emotion, playlist, etc.) |
| `emociones.py` | 7-category emotion detector (word-list + substring match) |
| `intenciones.py` | Intent matcher: number → stemming/synonyms → lexical fallback |
| `frases.py` | Phrase bank with history dedup |
| `spotify.py` | OAuth flow + search/playback via spotipy |
| `spotify_cache.py` | JSON-based playlist cache |

## FSM flow (`motor_fsm.py:procesar_texto`)

1. `detectar_emocion()` → updates session
2. `match_intencion()` → number match > keyword match > lexical match
3. `_evaluar_redireccion_emocional()` — if detected emotion is unexpected at current node AND alternative branches exist, redirect
4. Falls to `no_match` → clarification loop in frontend

## Emotion detection (`emociones.py`)

- Word lists per emotion; match via `_normalizar()` + `in` substring check
- `_normalizar()` lowercases, strips accents, keeps `[a-z0-9\s]` only
- **To add a word**: just append to the list (ensure it survives normalization)
- Duplicate `emocion_a_rama()` was a known bug (removed — keep only the first one returning `list[str]`)

## Intent matching (`intenciones.py`)

- Spanish stopwords list, custom stemmer (clitic removal, suffix stripping)
- Synonym expansion via `SINONIMOS` dict, n-gram similarity fallback
- Number matching: "primero/1/uno" → index 0, etc.
- Options use parenthetical keywords in their text: `"Option name (keyword1,keyword2)"`

## Emotional redirect

- `EMOCIONES_ESPERADAS_POR_NODO` in `motor_fsm.py` lists which emotions are expected per node
- If detected emotion not in expected set, and alternative branches exist → redirect
- Use `self.motor.obtener_mensaje_empatico()` to get an emotion-specific phrase
- `EMOCION_A_RAMA` in `emociones.py` maps emotions → destination nodes

## Config & env

- `.env` file loaded by `config.py`
- Keys: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`, `TELEGRAM_BOT_TOKEN`, `SPOTIFY_MARKET`
- Spotify OAuth redirect URI must be `http://localhost:8888/callback` in Spotify Dashboard

## Names & conventions

- **Emotion keys always with accents** in dicts (e.g. `"enojo"` not `"enojo"`), even though normalization removes them for matching
- **Node IDs**: `N01`–`N25` in `base_conocimiento.py`; leaf nodes (N17–N25) have `esHoja: true` and `spotify_query` for playlists
- **Theme toggle**: swaps moon/sun icons; `LIGHT`/`DARK` dicts in `desktop_gui.py`; no persistence between sessions
- **CRLF**: repo uses LF; Windows GUI files show warnings on `git add` — safe to ignore

## Build artifacts

- `.spec` file for PyInstaller
- Icon PNGs in `assets/` (also loaded by path at runtime)
- Build output in `dist/`, artifacts in `build/`
