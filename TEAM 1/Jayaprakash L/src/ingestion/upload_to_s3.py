import os
from pathlib import Path
from dotenv import load_dotenv
from src.aws.s3 import upload_file

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
csv_file = ROOT / "data" / "dataset.csv"
key = os.getenv("S3_RAW_PREFIX", "raw/vehicles/") + csv_file.name

print("Uploaded:", upload_file(str(csv_file), key))
