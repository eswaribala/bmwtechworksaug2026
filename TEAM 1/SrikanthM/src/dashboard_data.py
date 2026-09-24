from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_dashboard_summary(vehicle_summary_df: DataFrame, charging_df: DataFrame) -> DataFrame:
    charging_counts = (
        charging_df.groupBy("Vehicle_ID")
        .agg(F.count("*").alias("charging_frequency"), F.avg("Charging_Power_kW").alias("avg_charging_power_kw"))
    )

    return vehicle_summary_df.join(charging_counts, on="Vehicle_ID", how="left")
