from pyspark.sql import functions as F
from pyspark.sql.window import Window

def ranked_vehicles(df):
    w = Window.orderBy(F.col("overall_efficiency").desc_nulls_last())
    return df.withColumn("efficiency_rank", F.row_number().over(w))

def top_vehicles(df, n=5):
    return (
        df.filter(F.col("overall_efficiency").isNotNull())
        .orderBy(F.col("overall_efficiency").desc())
        .limit(n)
    )

def bottom_vehicles(df, n=5):
    return (
        df.filter(F.col("overall_efficiency").isNotNull())
        .orderBy(F.col("overall_efficiency").asc())
        .limit(n)
    )
