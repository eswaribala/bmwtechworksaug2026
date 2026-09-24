import logging
from pathlib import Path

from config.settings import LOG_LEVEL, PROJECT_ROOT


LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "bmw_analyst.log"


def configure_logging() -> logging.Logger:
    """
    Configure application logging.

    Logs are written to:
        logs/bmw_analyst.log
    """

    log_level = getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO,
    )

    logger = logging.getLogger("bmw_analyst")
    logger.setLevel(log_level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


logger = configure_logging()