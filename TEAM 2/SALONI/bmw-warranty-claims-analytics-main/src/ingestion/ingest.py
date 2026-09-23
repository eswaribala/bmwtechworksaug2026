import logging
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BUCKET_NAME = "bmw-warranty-claims-532404260630"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "sample"

FILES_TO_UPLOAD = {
    DATA_DIR / "warranty_claims.csv": "raw/warranty/warranty_claims.csv",
    DATA_DIR / "vehicle_master.csv": "raw/vehicle_master/vehicle_master.csv",
}


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# S3 Ingestion
# ---------------------------------------------------------

def upload_file_to_s3(s3_client, local_file: Path, s3_key: str) -> None:
    """Upload a local file to the configured S3 bucket."""

    if not local_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {local_file}"
        )

    logger.info(
        "Uploading %s -> s3://%s/%s",
        local_file,
        BUCKET_NAME,
        s3_key,
    )

    s3_client.upload_file(
        str(local_file),
        BUCKET_NAME,
        s3_key,
    )

    logger.info(
        "Successfully uploaded: s3://%s/%s",
        BUCKET_NAME,
        s3_key,
    )


def main() -> None:
    logger.info("Starting BMW Warranty Claims ingestion pipeline")

    try:
        s3_client = boto3.client("s3")

        for local_file, s3_key in FILES_TO_UPLOAD.items():
            upload_file_to_s3(
                s3_client,
                local_file,
                s3_key,
            )

        logger.info("BMW Warranty Claims ingestion completed successfully")

    except (FileNotFoundError, ClientError, BotoCoreError) as exc:
        logger.exception(
            "BMW Warranty Claims ingestion failed: %s",
            exc,
        )
        raise

    except Exception as exc:
        logger.exception(
            "Unexpected ingestion error: %s",
            exc,
        )
        raise


if __name__ == "__main__":
    main()