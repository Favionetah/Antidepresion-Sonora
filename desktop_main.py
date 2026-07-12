import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from desktop_gui import ChatbotSBCApp


def main() -> None:
    app = ChatbotSBCApp()
    app.ejecutar()


if __name__ == "__main__":
    main()
