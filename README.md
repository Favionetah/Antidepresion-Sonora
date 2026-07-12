# SBC Musicoterapia

Sistema Basado en Conocimiento (SBC) para diagnóstico adaptativo de estrés y prescripción personalizada de musicoterapia mediante Spotify.

Arquitectura híbrida: Aplicación de escritorio (CustomTkinter) + Bot de Telegram, compartiendo el mismo núcleo.

## Requisitos

- Python 3.10+
- pip

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

### 2. Telegram Bot (opcional - solo para modo Telegram)

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
│   └── spotify.py              # Integración Spotify API
├── desktop_gui.py              # Interfaz CustomTkinter
├── desktop_main.py             # Entry point escritorio
├── telegram_bot.py             # Bot de Telegram
├── telegram_main.py            # Entry point Telegram
├── oauth_callback_server.py    # Servidor OAuth multiusuario
├── config.py                   # Carga de variables de entorno
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

## Licencia

Uso educativo y personal.
