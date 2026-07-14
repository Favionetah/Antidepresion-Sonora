# Antidepresión Sonora — Musicoterapia

Sistema Basado en Conocimiento (SBC) para diagnóstico adaptativo de estrés y prescripción personalizada de musicoterapia mediante Spotify.

Arquitectura híbrida: **Aplicación de escritorio** (CustomTkinter) + **Bot de Telegram**, compartiendo el mismo núcleo FSM.

## Características

- Árbol de decisión de **25 nodos** en 5 niveles
- Diagnóstico emocional conversacional (síntomas físicos, mentales y emocionales)
- Prescripción automática de playlist vía **Spotify API**
- **Reproductor integrado** en escritorio con controles de playback (play/pause, anterior/siguiente, volumen, shuffle, repeat)
- **Polling en vivo** del estado de reproducción (canción, artista, portada, barra de progreso)
- Tema **oscuro/claro** con paleta Apple-crema y estilo neo-skeuomorphic
- **Bot de Telegram** con comandos `/nowplaying` y controles de reproducción inline
- Efecto de escritura simulado y animación de typing
- Multisesión: cada usuario de Telegram mantiene su propio estado FSM

## Requisitos

- Python 3.10+
- pip
- Cuenta de Spotify (Premium para reproducción controlada; Free para escuchar manualmente)

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Spotify API

1. Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Inicia sesión con tu cuenta de Spotify
3. Crea una nueva aplicación ("Create App")
4. Copia el **Client ID** y **Client Secret**
5. Agrega `http://localhost:8888/callback` en "Redirect URIs"
6. Copia `.env.example` a `.env` y completa las credenciales

### 2. Telegram Bot (opcional — solo para modo Telegram)

1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía `/newbot` y sigue las instrucciones
3. BotFather te dará un **token** (formato: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Copia el token a `TELEGRAM_BOT_TOKEN` en tu `.env`

### 3. Archivo .env

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

## Ejecución

### Aplicación de Escritorio

```bash
python desktop_main.py
```

### Bot de Telegram

```bash
python telegram_main.py
```

## Comandos de Telegram

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicia o reinicia la conversación |
| `/help` | Muestra la lista de comandos |
| `/reset` | Reinicia tu sesión de diagnóstico |
| `/spotify` | Conecta tu cuenta de Spotify u obtén la playlist |
| `/diagnostico` | Muestra tu diagnóstico actual |
| `/nowplaying` | Muestra la canción en reproducción con controles |

## Reproductor Integrado (Escritorio)

El reproductor aparece automáticamente al prescribir una playlist:

- **Portada del álbum** con máscara rounded
- **Barra de progreso** dorada en vivo
- **Controles**: play/pause, anterior, siguiente
- Compatible con **shuffle** y **repetición**
- Polling cada 3 segundos del estado de Spotify
- Se oculta automáticamente al reiniciar el diagnóstico

## Controles de Telegram

Al usar `/nowplaying` obtienes un teclado inline con:

- ⏮ Anterior / ⏸ Pausar / ▶️ Reanudar / ⏭ Siguiente
- 🔊 Subir volumen / 🔉 Bajar volumen
- 🔀 Alternar shuffle / 🔁 Alternar repetición
- 🔄 Actualizar estado

## Empaquetar .exe (Escritorio)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed desktop_main.py
```

El ejecutable estará en `dist/desktop_main.exe`.

## Estructura del Proyecto

```
chatBot_IA/
├── chatbot/                    # Paquete compartido (núcleo)
│   ├── __init__.py
│   ├── base_conocimiento.py    # 25 nodos (Singleton)
│   ├── motor_fsm.py            # FSM instanciable por usuario
│   ├── contexto.py             # Datos de sesión
│   ├── frases.py               # Banco de frases variables
│   └── spotify.py              # Integración Spotify API + control playback
├── desktop_gui.py              # Interfaz CustomTkinter (reproductor, temas, chat)
├── desktop_main.py             # Entry point escritorio
├── telegram_bot.py             # Bot de Telegram (comandos, callbacks, controles)
├── telegram_main.py            # Entry point Telegram
├── oauth_callback_server.py    # Servidor OAuth multiusuario
├── config.py                   # Carga de variables de entorno
├── assets/                     # Iconos PNG (128×128)
│   ├── play.png / pause.png / prev.png / next.png
│   ├── volume.png / shuffle.png / repeat.png
│   ├── spotify.png / send.png
│   ├── moon.png / sun.png
│   └── splash_logo.png
├── requirements.txt
├── .env.example
└── README.md
```

## Árbol de Decisión

El sistema utiliza 25 nodos organizados en 5 niveles:

| Nivel | Descripción | Nodos |
|-------|-------------|-------|
| 1 | Raíz (Inicio) | N01 |
| 2 | Síntomas principales | N02-N04 |
| 3 | Clasificación de estrés | N05-N10 |
| 4 | Enfoque de intervención | N11-N16 |
| 5 | Hojas (Playlists) | N17-N25 |

## Stack Tecnológico

- **Python 3.13** — Lenguaje principal
- **CustomTkinter** — GUI de escritorio con temas modernos
- **Pillow (PIL)** — Procesamiento de imágenes (portadas, fondos, splash)
- **Spotipy** — Cliente Python para la API de Spotify
- **python-telegram-bot** — Framework asíncrono para el bot de Telegram
- **pywin32** — Soporte de ventanas en Windows

## Licencia

Uso educativo y personal.
