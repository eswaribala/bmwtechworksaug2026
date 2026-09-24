from pathlib import Path

import boto3

from python.config import settings
from python.logger import get_logger

logger = get_logger(__name__)


class S3Ingestion:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION
        )

    def upload_file(self, local_file: str, s3_key: str) -> None:
        path = Path(local_file)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {local_file}")

        try:
            self.client.upload_file(
                str(path),
                settings.S3_BUCKET,
                s3_key
            )

            logger.info(
                "Uploaded %s to s3://%s/%s",
                local_file,
                settings.S3_BUCKET,
                s3_key
            )

        except Exception:
            logger.exception("S3 upload failed")
            raise

    def upload_telemetry(self, local_file: str) -> None:
        filename = Path(local_file).name

        self.upload_file(
            local_file,
            f"{settings.S3_RAW_PREFIX}/telemetry/{filename}"
        )

    def upload_sales(self, local_file: str) -> None:
        filename = Path(local_file).name

        self.upload_file(
            local_file,
            f"{settings.S3_RAW_PREFIX}/sales/{filename}"
        )

    def upload_vehicle(self, local_file: str) -> None:
        filename = Path(local_file).name

        self.upload_file(
            local_file,
            f"{settings.S3_RAW_PREFIX}/vehicle/{filename}"
        )

    def upload_dealer(self, local_file: str) -> None:
        filename = Path(local_file).name

        self.upload_file(
            local_file,
            f"{settings.S3_RAW_PREFIX}/dealer/{filename}"
        )