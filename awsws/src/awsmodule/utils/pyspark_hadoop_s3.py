from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("BMW S3")
    .master("local[*]")
    .config(
        "spark.jars.packages",
        "org.apache.hadoop:hadoop-aws:3.5.0"
    )
    .config(
        "spark.hadoop.fs.s3a.impl",
        "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        "s3.us-east-1.amazonaws.com"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

s3_path = (
    "s3a://bmw-s3-bucket-2026/connecteddata/bmw_connected_cars.csv"
)

df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(s3_path)
)

df.show(truncate=False)

print("Total rows:", df.count())

print("S3 READ SUCCESS")

spark.stop()