from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, upper, trim


def main():
    spark = (
        SparkSession.builder
        .appName("BMWTelemetryProcessing")
        .master("local[*]")
        .getOrCreate()
    )

    input_path = "data/telemetry/telemetry_initial.csv"

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(input_path)
    )

    print("Original data")
    df.show()

    clean_df = (
        df
        .filter(col("vehicle_id").isNotNull())
        .filter(col("battery_level").between(0, 100))
        .filter(col("speed") >= 0)
        .withColumn("model", upper(trim(col("model"))))
        .withColumn("region", upper(trim(col("region"))))
    )

    print("Cleaned data")
    clean_df.show()

    summary_df = (
        clean_df
        .groupBy("model", "region")
        .agg(
            count("vehicle_id").alias("vehicle_count"),
            avg("battery_level").alias("average_battery"),
            avg("temperature").alias("average_temperature"),
        )
    )

    print("BMW telemetry summary")
    summary_df.show()

    spark.stop()


if __name__ == "__main__":
    main()