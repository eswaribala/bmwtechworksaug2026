import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "config.toml"

with CONFIG_FILE.open("rb") as file:
    CONFIG = tomllib.load(file)


BOOTSTRAP_SERVERS = CONFIG["kafka"]["bootstrap_servers"]
TOPIC = CONFIG["kafka"]["topic"]
GROUP_ID = CONFIG["kafka"]["group_id"]
AUTO_OFFSET_RESET = CONFIG["kafka"]["auto_offset_reset"]
SOURCE_NAMESPACE = CONFIG["kafka"]["source_namespace"]

DATABASE_PATH = PROJECT_ROOT / CONFIG["storage"]["database_path"]