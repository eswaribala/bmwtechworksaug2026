from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def load_csv(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {file_path}")
    frame = pd.read_csv(file_path)
    logger.info("Loaded %s rows from %s", len(frame), file_path)
    return frame
