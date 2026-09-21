import logging
from pathlib import Path


# ============================================================
# LOG DIRECTORY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = LOG_DIR / "etl_pipeline.log"


# ============================================================
# LOGGER CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


# ============================================================
# APPLICATION LOGGER
# ============================================================

logger = logging.getLogger("BMW-ETL")