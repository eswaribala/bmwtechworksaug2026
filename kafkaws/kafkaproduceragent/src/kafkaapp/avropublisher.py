import os
from pathlib import Path
from dotenv import load_dotenv
import logging

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
SCHEMA_PATH = PROJECT_ROOT / "customer_schema.avsc"

load_dotenv(ENV_PATH)



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')