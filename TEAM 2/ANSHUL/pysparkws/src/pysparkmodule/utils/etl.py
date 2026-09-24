# ---------------------------------------------------------
# Create PySpark session
# ---------------------------------------------------------

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    year,
    month,
    trim,
    upper,
    initcap
)

from pyspark.sql.types import (
    StringType,
    IntegerType,
    DoubleType,
    DateType
)


def main() -> None:
    """Run the BMW sales ETL pipeline."""
    spark = SparkSession.builder \
        .appName("BMW Sales ETL Application") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .master("local[*]") \
        .getOrCreate()

    # ---------------------------------------------------------
    # Project paths
    # ---------------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    DATA_PATH = (
        PROJECT_ROOT
        / "src"
        / "pysparkmodule"
        / "data"
        / "bmw_sales_records.csv"
    )

    # ---------------------------------------------------------
    # Read sales data from CSV
    # ---------------------------------------------------------

    sales_df = spark.read.csv(
        str(DATA_PATH),
        header=True,
        inferSchema=True
    )

    print("\nRaw Data:")
    sales_df.show(10, truncate=False)

    print("\nRaw Schema:")
    sales_df.printSchema()

    # ---------------------------------------------------------
    # 1. DEFINE PROPER DATA TYPES
    # ---------------------------------------------------------

    sales_df = sales_df \
        .withColumn("sale_id", col("sale_id").cast(StringType())) \
        .withColumn("vehicle_id", col("vehicle_id").cast(StringType())) \
        .withColumn("dealer_id", col("dealer_id").cast(StringType())) \
        .withColumn("customer_id", col("customer_id").cast(StringType())) \
        .withColumn("sale_date", col("sale_date").cast(DateType())) \
        .withColumn("model", col("model").cast(StringType())) \
        .withColumn("region", col("region").cast(StringType())) \
        .withColumn("price", col("price").cast(DoubleType())) \
        .withColumn("quantity", col("quantity").cast(IntegerType()))

    # ---------------------------------------------------------
    # 2. HANDLE MISSING VALUES
    # ---------------------------------------------------------

    sales_df = sales_df.dropna(
        subset=[
            "sale_id",
            "vehicle_id",
            "dealer_id",
            "customer_id",
            "sale_date",
            "model",
            "region",
            "price",
            "quantity"
        ]
    )

    # ---------------------------------------------------------
    # 3. REMOVE DUPLICATE RECORDS
    # ---------------------------------------------------------

    sales_df = sales_df.dropDuplicates(["sale_id"])

    # ---------------------------------------------------------
    # 4. VALIDATE SALE ID
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "sale_id",
        when(
            trim(col("sale_id")) != "",
            trim(col("sale_id"))
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["sale_id"])

    # ---------------------------------------------------------
    # 5. VALIDATE VEHICLE ID
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "vehicle_id",
        when(
            trim(col("vehicle_id")) != "",
            trim(col("vehicle_id"))
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["vehicle_id"])

    # ---------------------------------------------------------
    # 6. VALIDATE DEALER ID
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "dealer_id",
        when(
            trim(col("dealer_id")) != "",
            trim(col("dealer_id"))
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["dealer_id"])

    # ---------------------------------------------------------
    # 7. VALIDATE CUSTOMER ID
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "customer_id",
        when(
            trim(col("customer_id")) != "",
            trim(col("customer_id"))
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["customer_id"])

    # ---------------------------------------------------------
    # 8. VALIDATE QUANTITY
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "quantity",
        when(
            col("quantity") > 0,
            col("quantity")
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["quantity"])

    # ---------------------------------------------------------
    # 9. VALIDATE PRICE
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "price",
        when(
            col("price") > 0,
            col("price")
        ).otherwise(None)
    )

    sales_df = sales_df.dropna(subset=["price"])



    # ---------------------------------------------------------
    # 10. CALCULATE REVENUE
    # ---------------------------------------------------------

    # Revenue is not present in the raw dataset.
    #
    # Revenue = price × quantity

    sales_df = sales_df.withColumn(
        "revenue",
        col("price") * col("quantity")
    )

    # ---------------------------------------------------------
    # 11. EXTRACT YEAR AND MONTH
    # ---------------------------------------------------------

    sales_df = sales_df \
        .withColumn(
            "sale_year",
            year(col("sale_date"))
        ) \
        .withColumn(
            "sale_month",
            month(col("sale_date"))
        )

    # ---------------------------------------------------------
    # 12. STANDARDIZE MODEL
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "model",
        upper(trim(col("model")))
    )

    # ---------------------------------------------------------
    # 13. STANDARDIZE REGION
    # ---------------------------------------------------------

    sales_df = sales_df.withColumn(
        "region",
        initcap(trim(col("region")))
    )

    # ---------------------------------------------------------
    # 14. STANDARDIZE IDs
    # ---------------------------------------------------------

    sales_df = sales_df \
        .withColumn("vehicle_id", upper(trim(col("vehicle_id")))) \
        .withColumn("dealer_id", upper(trim(col("dealer_id")))) \
        .withColumn("customer_id", upper(trim(col("customer_id"))))

    # ---------------------------------------------------------
    # 15. FINAL COLUMN SELECTION
    # ---------------------------------------------------------

    sales_df = sales_df.select(
        "sale_id",
        "vehicle_id",
        "dealer_id",
        "customer_id",
        "sale_date",
        "sale_year",
        "sale_month",
        "model",
        "region",
        "price",
        "quantity",
        "revenue"
    )

    # ---------------------------------------------------------
    # Display cleaned data
    # ---------------------------------------------------------

    print("\nCleaned Data:")
    sales_df.show(20, truncate=False)

    # ---------------------------------------------------------
    # Display final schema
    # ---------------------------------------------------------

    print("\nFinal Schema:")
    sales_df.printSchema()

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    print("\nTotal Cleaned Records:")
    print(sales_df.count())

    print("\nDuplicate sale IDs:")
    duplicate_sale_ids = (
        sales_df
        .groupBy("sale_id")
        .count()
        .filter(col("count") > 1)
        .count()
    )
    print(duplicate_sale_ids)

    print("\nInvalid quantity:")
    print(sales_df.filter(col("quantity") <= 0).count())

    print("\nInvalid price:")
    print(sales_df.filter(col("price") <= 0).count())

    print("\nInvalid revenue:")
    print(sales_df.filter(col("revenue") != col("price") * col("quantity")).count())

    print("\nNull values:")
    for column in sales_df.columns:
        null_count = sales_df.filter(col(column).isNull()).count()
        print(f"{column}: {null_count}")

    # ---------------------------------------------------------
    # Save cleaned data as Parquet
    # ---------------------------------------------------------

    OUTPUT_PATH = (
        PROJECT_ROOT
        / "src"
        / "pysparkmodule"
        / "data"
        / "bmw_sales_cleaned.parquet"
    )

    sales_df.toPandas().to_parquet(str(OUTPUT_PATH), index=False)

    print("\nCleaned data saved successfully!")
    print(f"Output file: {OUTPUT_PATH}")

    # ---------------------------------------------------------
    # Show PySpark UI
    # ---------------------------------------------------------

    print("\nPySpark UI is available at: http://localhost:4040")
    input("Press Enter to exit...")
    spark.stop()


if __name__ == "__main__":
    main()