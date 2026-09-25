import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bucket_name: str = os.getenv(
        "BMW_BUCKET_NAME", "bmw-executive-analytics-dashboard-pattabhi"
    )
    aws_region: str = os.getenv("AWS_REGION", "eu-central-1")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
