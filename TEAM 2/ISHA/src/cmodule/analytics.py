from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# ====================================
# Spark Session
# ====================================

spark = (
    SparkSession.builder
    .appName("BMW_Service_Centre_Analytics")
    .getOrCreate()
)

# ====================================
# Read Joined Dataset
# ====================================

df = spark.read.csv(
    "maintenance_dealer_joined.csv",
    header=True,
    inferSchema=True
)

# ====================================
# KPI 1
# Services Per Dealer
# ====================================

services_df = (
    df
    .groupBy(
        "dealer_id",
        "dealer_name",
        "city",
        "region",
        "capacity"
    )
    .agg(
        count("*").alias("total_services")
    )
)

# ====================================
# KPI 2
# Average Repair Cost
# ====================================

repair_df = (
    df
    .groupBy("dealer_id")
    .agg(
        round(
            avg("repair_cost"),
            2
        ).alias("avg_repair_cost")
    )
)

# ====================================
# KPI 3
# Average Service Interval
# ====================================

window_spec = (
    Window.partitionBy("vehicle_id")
    .orderBy("service_date")
)

interval_df = (
    df
    .withColumn(
        "previous_service_date",
        lag("service_date").over(window_spec)
    )
    .withColumn(
        "service_interval_days",
        datediff(
            col("service_date"),
            col("previous_service_date")
        )
    )
)

interval_avg_df = (
    interval_df
    .groupBy("dealer_id")
    .agg(
        round(
            avg("service_interval_days"),
            2
        ).alias(
            "avg_service_interval_days"
        )
    )
)

# ====================================
# Capacity Utilization
# ====================================

final_df = (
    services_df
    .join(
        repair_df,
        "dealer_id"
    )
    .join(
        interval_avg_df,
        "dealer_id"
    )
)

final_df = (
    final_df
    .withColumn(
        "capacity_utilization_pct",
        round(
            (
                col("total_services")
                * 100
            )
            / col("capacity"),
            2
        )
    )
)

# ====================================
# Dealer Status
# ====================================

final_df = (
    final_df
    .withColumn(
        "dealer_status",
        when(
            col(
                "capacity_utilization_pct"
            ) > 90,
            "OVERLOADED"
        )
        .when(
            col(
                "capacity_utilization_pct"
            ) < 60,
            "UNDER_UTILIZED"
        )
        .otherwise(
            "OPTIMAL"
        )
    )
)

# ====================================
# Regional Ranking
# ====================================

rank_window = (
    Window.partitionBy("region")
    .orderBy(
        desc(
            "capacity_utilization_pct"
        )
    )
)

final_df = (
    final_df
    .withColumn(
        "regional_rank",
        rank().over(rank_window)
    )
)

# ====================================
# Export KPI Dataset
# ====================================

final_df.toPandas().to_csv(
    "dealer_capacity_metrics.csv",
    index=False
)

print("\nAnalytics Completed")
print("dealer_capacity_metrics.csv created")

# ====================================
# Top 10 Dealers
# ====================================

final_df.orderBy(
    desc(
        "capacity_utilization_pct"
    )
).show(
    10,
    truncate=False
)

spark.stop()