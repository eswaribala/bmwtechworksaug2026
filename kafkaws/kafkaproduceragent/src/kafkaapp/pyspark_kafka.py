from pathlib import Path
from dotenv import load_dotenv
import logging
import os
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
KRAFT_BOOTSTRAP_SERVERS = os.getenv("KRAFT_BOOTSTRAP_SERVERS")
KAFKA_AVRO_TOPIC = os.getenv("KAFKA_AVRO_TOPIC")