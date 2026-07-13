import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from chatbot import MotorFSM, SesionSBC
from chatbot import spotify
from chatbot.frases import (
    construir_mensaje_confirmacion,
    construir_mensaje_empatico,
    construir_clarificacion_empatica,
    construir_mensaje_feedback,
)

logger = logging.getLogger(__name__)

SESIONES: dict[int, SesionSBC] = {}
FALLOS: dict[int, int] = {}
ESPERANDO_FEEDBACK: dict[int, bool] = {}


def _obtener_sesion(chat_id: int) -> SesionSBC:
    if chat_id not in SESIONES:
        SESIONES[chat_id] = SesionSBC()
    return SESIONES[chat_id]


def _obtener_motor(chat_id: int) -> MotorFSM:
    sesion = _obtener_sesion(chat_id)
    return MotorFSM(sesion)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in SESIONES:
        SESIONES[chat_id].reiniciar()
    FALLOS[chat_id] = 0
    ESPERANDO_FEEDBACK[chat_id] = False
    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)
    mensaje = motor.obtener_pregunta()
    opciones = motor.obtener_opciones()
    reply_markup = _construir_teclado_opciones(opciones) if opciones else None
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
        "Cuéntame cómo te sientes con tus propias palabras. "
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
        "*Arquitectura:* Clean Architecture + FSM + SBC + Emociones"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in SESIONES:
        SESIONES[chat_id].reiniciar()
    FALLOS[chat_id] = 0
    ESPERANDO_FEEDBACK[chat_id] = False
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    texto = update.message.text.strip()
    if not texto:
        return

    if chat_id not in SESIONES:
        SESIONES[chat_id] = SesionSBC()
        FALLOS[chat_id] = 0
        ESPERANDO_FEEDBACK[chat_id] = False
        motor = MotorFSM(SESIONES[chat_id])
        mensaje = motor.obtener_pregunta()
        await update.message.reply_text(mensaje)
        return

    if ESPERANDO_FEEDBACK.get(chat_id):
        ESPERANDO_FEEDBACK[chat_id] = False
        SESIONES[chat_id].feedback_recomendacion = texto
        await update.message.reply_text(
            "Gracias por tu opinión. Me ayuda a mejorar las recomendaciones para ti.\n\n"
            "¿Quieres realizar otro diagnóstico? Usa /start para comenzar de nuevo."
        )
        return

    sesion = _obtener_sesion(chat_id)
    motor = MotorFSM(sesion)
    resultado = motor.procesar_texto(texto)

    if resultado["tipo"] == "opcion":
        FALLOS[chat_id] = 0
        await _ejecutar_opcion(update.message, motor, sesion, resultado["indice"])
    elif resultado["tipo"] == "redireccion":
        FALLOS[chat_id] = 0
        await _manejar_redireccion(update.message, motor, resultado["sugerencia"])
    else:
        FALLOS[chat_id] = FALLOS.get(chat_id, 0) + 1
        await _pedir_clarificacion(update.message, motor, sesion)


async def _ejecutar_opcion(
    message, motor: MotorFSM, sesion: SesionSBC, indice: int
) -> None:
    opcion = motor.obtener_info_opcion(indice)
    if not opcion:
        await message.reply_text(
            "Esta opción ya no está disponible. Usa /start para comenzar de nuevo."
        )
        return

    texto_opcion = opcion["texto"]
    destino = motor.transicionar(indice)
    if not destino:
        await message.reply_text(
            "Hubo un error al procesar tu respuesta. Usa /start para reiniciar."
        )
        return

    nodo_origen = motor.obtener_nodo_actual()
    confirmacion = construir_mensaje_confirmacion(
        nodo_origen, sesion, texto_opcion
    )

    if motor.es_nodo_hoja():
        await _procesar_nodo_hoja(message, motor, sesion, confirmacion)
    else:
        nuevo_mensaje = motor.obtener_pregunta()
        opciones = motor.obtener_opciones()
        reply_markup = _construir_teclado_opciones(opciones) if opciones else None
        await message.reply_text(f"{confirmacion}\n\n{nuevo_mensaje}", reply_markup=reply_markup)


async def _procesar_nodo_hoja(
    message, motor: MotorFSM, sesion: SesionSBC, confirmacion: str
) -> None:
    diagnostico = motor.obtener_diagnostico()
    await message.reply_text(f"{confirmacion}\n\n{diagnostico}", parse_mode="Markdown")

    nodo = motor.obtener_nodo_actual()
    if not nodo.get("spotify_query"):
        await message.reply_text(
            "¿Quieres realizar otro diagnóstico? Usa /start para comenzar de nuevo."
        )
        return

    resultado = spotify.resolver_playlist(nodo)
    if resultado:
        sesion.playlist_recomendada = resultado
        playlist_msg = (
            f"🎵 *Playlist recomendada:*\n"
            f"{resultado.get('nombre', '')}\n"
            f"{resultado.get('url', '')}"
        )
        reply_markup = _construir_teclado_acciones(
            resultado.get("url", ""),
            bool(sesion.token_spotify),
        )
        await message.reply_text(
            playlist_msg, parse_mode="Markdown",
            reply_markup=reply_markup,
        )

        sesion.registrar_recomendacion(resultado)
        await _preguntar_feedback(message)
    else:
        await message.reply_text(
            "No pude obtener la playlist en este momento. "
            "Intenta de nuevo más tarde con /spotify.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Nuevo diagnóstico", callback_data="nuevo_diagnostico")
            ]]),
        )


async def _preguntar_feedback(message) -> None:
    chat_id = message.chat.id
    msg = construir_mensaje_feedback()
    ESPERANDO_FEEDBACK[chat_id] = True
    await message.reply_text(msg)


async def _pedir_clarificacion(
    message, motor: MotorFSM, sesion: SesionSBC
) -> None:
    chat_id = message.chat.id
    fallos = FALLOS.get(chat_id, 0)
    nodo = motor.obtener_nodo_actual()
    opciones = nodo.get("opciones", [])
    if not opciones:
        return

    if fallos == 1:
        empatica = construir_clarificacion_empatica(sesion, opciones)
        if empatica:
            msg = empatica
        else:
            mensaje_empatico = motor.obtener_mensaje_empatico()
            if mensaje_empatico:
                msg = mensaje_empatico
            else:
                msg = "Cuéntame un poco más para entenderte mejor."
    elif fallos == 2:
        textos = [o["texto"].split("(")[0].strip().lower() for o in opciones]
        n = len(textos)
        emotion = sesion.emotion_principal
        if emotion != "neutral":
            if n == 1:
                msg = f"Por lo que dices, ¿{textos[0]} describe lo que sientes?"
            elif n == 2:
                msg = f"¿Lo que sientes se parece más a {textos[0]} o a {textos[1]}?"
            else:
                msg = f"¿Lo que sientes se acerca más a {textos[0]}, {textos[1]} o {textos[2]}?"
        else:
            if n == 1:
                msg = f"¿Te parece que {textos[0]} describe lo que sientes?"
            elif n == 2:
                msg = f"Déjame preguntarte de otra forma. ¿Lo que sientes es más {textos[0]} o {textos[1]}?"
            else:
                msg = f"Déjame preguntarte de otra forma. ¿Lo que sientes es más {textos[0]}, {textos[1]} o {textos[2]}?"
    else:
        palabras_clave = []
        for o in opciones:
            parentesis = o["texto"].split("(")
            if len(parentesis) > 1:
                palabras = parentesis[1].rstrip(")").split(",")
                palabras_clave.extend(p.strip() for p in palabras[:2])
        if palabras_clave:
            ejemplos = ", ".join(palabras_clave[:4])
            msg = (
                "Para ayudarte mejor, dime si alguna de estas palabras "
                f"resuena con lo que sientes: {ejemplos}."
            )
        else:
            msg = "Cuéntame con tus palabras cómo te sientes."
    await message.reply_text(msg)


async def _manejar_redireccion(
    message, motor: MotorFSM, sugerencia: dict
) -> None:
    destinos = sugerencia.get("destinos", [])
    opciones = motor.obtener_opciones()
    nombres = []
    for i, o in enumerate(opciones):
        if o.get("destino", "") in destinos:
            nombres.append(o["texto"].split("(")[0].strip().lower())
    if nombres:
        if len(nombres) > 1:
            opciones_str = " o ".join(nombres)
            msg = (
                f"Por cómo te expresas, lo que cuentas parece más cercano a "
                f"{opciones_str}. ¿Cuál resuena más contigo?"
            )
        else:
            msg = (
                f"Por cómo te expresas, parece que estás experimentando "
                f"algo más de tipo emocional. "
                f"¿Te parece que {nombres[0]} describe mejor lo que sientes?"
            )
    else:
        msg = "Cuéntame un poco más para entenderte mejor."
    await message.reply_text(msg)


def _construir_teclado_opciones(opciones: list[dict]) -> InlineKeyboardMarkup:
    teclado = []
    for i, opcion in enumerate(opciones):
        destino = opcion.get("destino", "")
        teclado.append([InlineKeyboardButton(opcion["texto"], callback_data=f"opt:{i}:{destino}")])
    return InlineKeyboardMarkup(teclado)


def _construir_teclado_acciones(url: str, tiene_token: bool) -> InlineKeyboardMarkup:
    teclado = []
    if url:
        teclado.append([InlineKeyboardButton("Abrir en Spotify", url=url)])
    if tiene_token:
        teclado.append([InlineKeyboardButton("Reproducir ahora", callback_data="play_now")])
    teclado.append([InlineKeyboardButton("Nuevo diagnóstico", callback_data="nuevo_diagnostico")])
    return InlineKeyboardMarkup(teclado)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    data = query.data

    if data.startswith("opt:"):
        partes = data.split(":")
        if len(partes) >= 2:
            try:
                indice = int(partes[1])
                sesion = _obtener_sesion(chat_id)
                motor = MotorFSM(sesion)
                await _ejecutar_opcion(query.message, motor, sesion, indice)
            except (ValueError, IndexError):
                await query.edit_message_text("Opción no válida. Usa /start para reiniciar.")
        return

    if data == "nuevo_diagnostico":
        if chat_id in SESIONES:
            SESIONES[chat_id].reiniciar()
        FALLOS[chat_id] = 0
        ESPERANDO_FEEDBACK[chat_id] = False
        sesion = _obtener_sesion(chat_id)
        motor = MotorFSM(sesion)
        mensaje = motor.obtener_pregunta()
        await query.edit_message_text(mensaje)
        return

    if data == "play_now":
        sesion = _obtener_sesion(chat_id)
        if not sesion.token_spotify or not sesion.playlist_recomendada:
            await query.edit_message_text(
                "No se pudo reproducir. Conecta tu cuenta con /spotify primero.",
            )
            return
        try:
            sp = spotify.crear_cliente(sesion.token_spotify)
            uri = f"spotify:playlist:{sesion.playlist_recomendada['id']}"
            res = spotify.reproducir_playlist(sp, uri)
            if res["resultado"] == "ok":
                await query.edit_message_text("Reproduciendo en tu dispositivo activo 🎧")
            elif res["resultado"] == "no_device":
                await query.edit_message_text(
                    "No encontré un dispositivo activo. Abre Spotify en tu celular "
                    "o computadora y selecciona una canción primero."
                )
            elif res["resultado"] == "free_account":
                await query.edit_message_text(
                    "Tu cuenta de Spotify es Free y no permite "
                    "reproducción remota. Abre el enlace de la playlist."
                )
            else:
                await query.edit_message_text(
                    "Hubo un error al reproducir. Abre Spotify manualmente."
                )
        except Exception as e:
            logger.error(f"Error reproducción callback: {e}")
            await query.edit_message_text(
                "Error al reproducir. Intenta abrir Spotify manualmente."
            )
        return


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error en update {update}: {context.error}")
    try:
        if update and update.effective_chat:
            await update.effective_chat.send_message(
                "Ocurrió un error inesperado. Por favor, usa /start para reiniciar."
            )
    except Exception:
        pass
