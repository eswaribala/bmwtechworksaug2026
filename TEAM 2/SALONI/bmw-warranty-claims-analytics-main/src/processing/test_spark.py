from pyspark.sql import SparkSession


def main():
    spark = (
        SparkSession.builder
        .appName("BMWWarrantySparkTest")
        .master("local[*]")
        .getOrCreate()
    )

    print("=" * 60)
    print("PySpark is working!")
    print("Spark version:", spark.version)
    print("=" * 60)

    data = [
        ("BMWV0001", "Engine", 2500.00),
        ("BMWV0002", "Battery", 1200.00),
        ("BMWV0003", "Transmission", 3500.00),
    ]

    columns = [
        "vehicle_id",
        "component",
        "claim_amount",
    ]

    df = spark.createDataFrame(data, columns)

    df.show()

    spark.stop()


if __name__ == "__main__":
    main()