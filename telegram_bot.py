import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from chatbot import MotorFSM, SesionSBC
from chatbot import spotify
from chatbot.frases import construir_mensaje_confirmacion

logger = logging.getLogger(__name__)

SESIONES: dict[int, SesionSBC] = {}


def _obtener_sesion(chat_id: int) -> SesionSBC:
    if chat_id not in SESIONES:
        SESIONES[chat_id] = SesionSBC()
    return SESIONES[chat_id]


def _obtener_motor(chat_id: int) -> MotorFSM:
    sesion = _obtener_sesion(chat_id)
    return MotorFSM(sesion)


def _construir_teclado(opciones: list[dict]) -> InlineKeyboardMarkup:
    teclado = []
    for i, opcion in enumerate(opciones):
        destino = opcion.get("destino", "")
        callback_data = f"goto:{destino}:{i}"
        teclado.append([InlineKeyboardButton(opcion["texto"], callback_data=callback_data)])
    return InlineKeyboardMarkup(teclado)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in SESIONES:
        SESIONES[chat_id].reiniciar()
    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)
    mensaje = motor.obtener_pregunta()
    opciones = motor.obtener_opciones()
    reply_markup = _construir_teclado(opciones) if opciones else None
    await update.message.reply_text(mensaje, reply_markup=reply_markup)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "🤖 *¿Cómo funciona este bot?*\n\n"
        "Soy un asistente de bienestar que te ayuda a encontrar la música "
        "ideal para tu estado de ánimo mediante un diagnóstico conversacional.\n\n"
        "*Comandos:*\n"
        "/start - Iniciar o reiniciar diagnóstico\n"
        "/help - Ver esta ayuda\n"
        "/about - Información del proyecto\n"
        "/reset - Reiniciar tu sesión\n"
        "/spotify - Obtener playlist o conectar Spotify\n"
        "/diagnostico - Ver tu diagnóstico actual\n\n"
        "Responde a las preguntas tocando los botones. "
        "Al final recibirás una playlist recomendada personalizada."
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "🎵 *SBC Musicoterapia*\n\n"
        "Sistema Basado en Conocimiento para diagnóstico adaptativo de estrés\n"
        "y prescripción personalizada de musicoterapia mediante Spotify.\n\n"
        "*Versión:* 2.0 (Fase 2 - Integración Híbrida)\n"
        "*Desarrollado con:* Python, CustomTkinter, python-telegram-bot, Spotipy\n"
        "*Arquitectura:* Clean Architecture + FSM + SBC"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in SESIONES:
        SESIONES[chat_id].reiniciar()
    await update.message.reply_text(
        "Tu sesión ha sido reiniciada. Usa /start para comenzar de nuevo."
    )


async def cmd_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)

    if sesion.token_spotify:
        if sesion.playlist_recomendada:
            pl = sesion.playlist_recomendada
            texto = (
                f"🎵 *Playlist recomendada:*\n"
                f"{pl.get('nombre', '')}\n\n"
                f"{pl.get('url', '')}"
            )
            await update.message.reply_text(texto, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                "Completa primero el diagnóstico para obtener una recomendación."
            )
        return

    try:
        oauth = spotify.crear_oauth()
        auth_url = oauth.get_authorize_url(state=str(chat_id))
        texto = (
            "Para conectar tu cuenta de Spotify y obtener recomendaciones personalizadas, "
            "autoriza el acceso aquí:\n\n"
            f"[Conectar mi cuenta de Spotify]({auth_url})"
        )
        await update.message.reply_text(texto, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error al generar URL de Spotify: {e}")
        await update.message.reply_text(
            "Hubo un error al conectar con Spotify. Intenta de nuevo más tarde."
        )


async def cmd_diagnostico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)

    if not sesion.historial_nodos:
        await update.message.reply_text(
            "Aún no has iniciado un diagnóstico. Usa /start para comenzar."
        )
        return

    if motor.es_nodo_hoja():
        diagnostico = motor.obtener_diagnostico()
        await update.message.reply_text(diagnostico, parse_mode="Markdown")
    else:
        resumen = (
            f"*Progreso del diagnóstico:*\n"
            f"• Nodo actual: {sesion.nodo_actual}\n"
            f"• Pasos completados: {len(sesion.historial_nodos)}\n"
            f"• Síntomas registrados: {sesion.sintomas_principales or 'En curso'}\n\n"
            "Continúa respondiendo las preguntas para obtener tu diagnóstico completo."
        )
        await update.message.reply_text(resumen, parse_mode="Markdown")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    data = query.data

    if not data.startswith("goto:"):
        return

    partes = data.split(":")
    if len(partes) < 3:
        return

    _, destino, idx_str = partes[:3]
    indice = int(idx_str)

    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)

    opcion = motor.obtener_info_opcion(indice)
    if not opcion:
        await query.edit_message_text(
            "Esta opción ya no está disponible. Usa /start para comenzar de nuevo."
        )
        return

    motor.transicionar(indice)

    if motor.es_nodo_hoja():
        await _procesar_nodo_hoja(query, motor, sesion)
    else:
        await _procesar_nodo_decision(query, motor, opcion)


async def _procesar_nodo_decision(
    query, motor: MotorFSM, opcion: dict
) -> None:
    mensaje = motor.obtener_pregunta()
    opciones = motor.obtener_opciones()
    reply_markup = _construir_teclado(opciones) if opciones else None

    texto_respuesta = f"{opcion['texto']}\n\n{mensaje}"
    await query.edit_message_text(texto_respuesta, reply_markup=reply_markup)


async def _procesar_nodo_hoja(
    query, motor: MotorFSM, sesion: SesionSBC
) -> None:
    diagnostico = motor.obtener_diagnostico()
    mensaje_base = f"{diagnostico}"

    await query.edit_message_text(mensaje_base, parse_mode="Markdown")

    nodo = motor.obtener_nodo_actual()
    if nodo.get("spotify_query"):
        resultado = spotify.resolver_playlist(nodo)
        if resultado:
            sesion.playlist_recomendada = resultado
            playlist_msg = (
                f"🎵 *Playlist recomendada:*\n"
                f"{resultado.get('nombre', '')}\n"
                f"{resultado.get('url', '')}"
            )
            await query.message.reply_text(playlist_msg, parse_mode="Markdown")

            if sesion.token_spotify:
                try:
                    sp = spotify.crear_cliente(sesion.token_spotify)
                    uri = f"spotify:playlist:{resultado['id']}"
                    resultado = spotify.reproducir_playlist(sp, uri)
                    if resultado == "ok":
                        await query.message.reply_text("Reproduciendo en tu dispositivo activo 🎧")
                    elif resultado == "no_device":
                        await query.message.reply_text(
                            "Para reproducir automáticamente, abre Spotify en tu "
                            "celular o computadora y selecciona una canción."
                        )
                except Exception as e:
                    logger.error(f"Error reproducción Telegram: {e}")
        else:
            await query.message.reply_text(
                "No pude obtener la playlist en este momento. "
                "Intenta de nuevo más tarde con /spotify."
            )

    await query.message.reply_text(
        "¿Quieres realizar otro diagnóstico? Usa /start para comenzar de nuevo."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error en update {update}: {context.error}")
    try:
        if update and update.effective_chat:
            await update.effective_chat.send_message(
                "Ocurrió un error inesperado. Por favor, usa /start para reiniciar."
            )
    except Exception:
        pass
