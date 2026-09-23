from pyspark.sql import SparkSession

def create_spark(app_name="EV-Range-Analytics"):
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions","4")
        .getOrCreate()
    )
