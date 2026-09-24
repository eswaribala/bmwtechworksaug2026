import argparse

import pandas as pd

from python.data_validation import validate_sales, validate_telemetry
from python.logger import get_logger
from python.s3_ingestion import S3Ingestion

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="BMW data ingestion pipeline"
    )

    parser.add_argument(
        "--type",
        choices=["telemetry", "sales", "vehicle", "dealer"],
        required=True
    )

    parser.add_argument(
        "--file",
        required=True
    )

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    ingestion = S3Ingestion()

    if args.type == "telemetry":
        validate_telemetry(df)
        ingestion.upload_telemetry(args.file)

    elif args.type == "sales":
        validate_sales(df)
        ingestion.upload_sales(args.file)

    elif args.type == "vehicle":
        ingestion.upload_vehicle(args.file)

    elif args.type == "dealer":
        ingestion.upload_dealer(args.file)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()