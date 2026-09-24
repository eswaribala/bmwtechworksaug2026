"""Ranking helpers for vehicle efficiency analysis.

The module provides both a reusable window-based rank and simple top/bottom
selection functions for dashboard and reporting outputs.
"""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

def ranked_vehicles(df):
    """Add a global efficiency rank using a Spark window."""
    w = Window.orderBy(F.col("overall_efficiency").desc_nulls_last())
    return df.withColumn("efficiency_rank", F.row_number().over(w))

def top_vehicles(df, n=5):
    """Return the highest-efficiency vehicles."""
    return (
        df.filter(F.col("overall_efficiency").isNotNull())
        .orderBy(F.col("overall_efficiency").desc())
        .limit(n)
    )

def bottom_vehicles(df, n=5):
    """Return the lowest-efficiency vehicles."""
    return (
        df.filter(F.col("overall_efficiency").isNotNull())
        .orderBy(F.col("overall_efficiency").asc())
        .limit(n)
    )
