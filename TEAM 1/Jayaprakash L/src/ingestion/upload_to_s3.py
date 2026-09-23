"""Upload the project's raw telemetry CSV to Amazon S3.

The target bucket and raw prefix are read from environment variables. The
module is intended for the AWS ingestion step and reuses the shared S3
client helper from :mod:`src.aws.s3`.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.aws.s3 import upload_file

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
csv_file = ROOT / "data" / "dataset.csv"
key = os.getenv("S3_RAW_PREFIX", "raw/vehicles/") + csv_file.name

def main():
    """Upload the project telemetry CSV to the configured S3 raw prefix."""
    print("Uploaded:", upload_file(str(csv_file), key))


if __name__ == "__main__":
    # Only perform an AWS upload when this file is executed directly.
    # Sphinx imports modules during autodoc generation, so importing this
    # module must never perform network operations or require AWS settings.
    main()
