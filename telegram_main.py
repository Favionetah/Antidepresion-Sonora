import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from config import TELEGRAM_BOT_TOKEN, OAUTH_HOST, OAUTH_PORT
from telegram_bot import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    cmd_start,
    cmd_help,
    cmd_about,
    cmd_reset,
    cmd_spotify,
    cmd_diagnostico,
    callback_handler,
    error_handler,
)
from oauth_callback_server import iniciar_servidor_oauth


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN no está configurado. "
            "Crea un archivo .env con tu token."
        )
        return

    servidor_thread = threading.Thread(
        target=iniciar_servidor_oauth,
        args=(OAUTH_HOST, OAUTH_PORT),
        daemon=True,
    )
    servidor_thread.start()
    logger.info(f"Servidor OAuth iniciado en {OAUTH_HOST}:{OAUTH_PORT}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("spotify", cmd_spotify))
    app.add_handler(CommandHandler("diagnostico", cmd_diagnostico))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(error_handler)

    logger.info("Bot de Telegram iniciado. Presiona Ctrl+C para detener.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
