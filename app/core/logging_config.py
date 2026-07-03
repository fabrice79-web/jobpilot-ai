import logging


def setup_logging() -> None:
    """Configure le système de logs de l'application."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )