# 06. Data Processing

## Local processing flow
1. Generate synthetic CSV data.
2. Validate schema and values.
3. Clean invalid records and write rejected outputs.
4. Convert to Parquet.
5. Partition by year/month.
6. Write to curated data location.

## Why parquet and partitioning matter
Parquet is columnar and efficient for analytical read patterns. Partitioning reduces the amount of data scanned for time-filtered queries.
