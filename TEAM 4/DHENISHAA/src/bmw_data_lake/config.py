"""Project configuration and environment-aware settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProjectConfig:
    """Application configuration for local and AWS-friendly execution."""

    project_name: str = "bmw-serverless-data-lake"
    environment: str = "dev"
    aws_region: str = "us-east-1"
    data_bucket_name: str = "bmw-data-lake-dev"  # placeholder value for config documentation
    raw_prefix: str = "raw"
    curated_prefix: str = "curated"
    logs_prefix: str = "logs"
    rejected_prefix: str = "rejected"

    @classmethod
    def from_env(cls) -> "ProjectConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "bmw-serverless-data-lake"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            data_bucket_name=os.getenv("DATA_BUCKET_NAME", "bmw-data-lake-dev"),
        )


DEFAULT_CONFIG = ProjectConfig.from_env()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_GENERATED_DIR = DATA_DIR / "generated"
DEFAULT_SAMPLE_DIR = DATA_DIR / "sample"
