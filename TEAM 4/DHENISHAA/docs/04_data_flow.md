# 04. Data Flow

## Flow
1. Generate synthetic BMW datasets.
2. Save raw CSV files to the local data directory.
3. Validate and transform data.
4. Write curated Parquet files to the curated S3 prefix.
5. Run Glue crawler to register schemas.
6. Query via Athena.
7. Visualize via QuickSight.

## Data lineage
The raw layer preserves original source records. The curated layer contains validation, cleanup, and structure-optimized files ready for analytics.
