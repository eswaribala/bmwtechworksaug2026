import os
import pandas as pd

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

os.makedirs(PROCESSED_PATH, exist_ok=True)


def validate_and_process(file_name):

    file_path = os.path.join(RAW_PATH, file_name)

    print(f"\nProcessing {file_name}")

    df = pd.read_csv(file_path)

    original_count = len(df)

    # Remove duplicates
    duplicates = df.duplicated().sum()
    df = df.drop_duplicates()

    # Count Nulls
    null_count = df.isnull().sum().sum()

    print(f"Original Records : {original_count}")
    print(f"Duplicates Found : {duplicates}")
    print(f"Null Values Found: {null_count}")

    output_file = os.path.join(
        PROCESSED_PATH,
        file_name
    )

    df.to_csv(output_file, index=False)

    print(f"Saved -> {output_file}")


FILES = [
    "vehicle_master.csv",
    "telemetry.csv",
    "maintenance.csv",
]

for file in FILES:
    validate_and_process(file)

print("\nIngestion Completed Successfully")