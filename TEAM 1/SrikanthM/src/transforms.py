from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def clean_telemetry(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("Timestamp", F.to_timestamp("Timestamp", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("SoC_Percent", F.col("SoC_Percent").cast("double"))
        .withColumn("SoH_Percent", F.col("SoH_Percent").cast("double"))
        .withColumn("Battery_Voltage_V", F.col("Battery_Voltage_V").cast("double"))
        .withColumn("Battery_Current_A", F.col("Battery_Current_A").cast("double"))
        .withColumn("Battery_Temperature_C", F.col("Battery_Temperature_C").cast("double"))
        .withColumn("Charging_Power_kW", F.col("Charging_Power_kW").cast("double"))
        .withColumn("Vehicle_Speed_kmh", F.col("Vehicle_Speed_kmh").cast("double"))
        .withColumn("Odometer_km", F.col("Odometer_km").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Timestamp", "SoH_Percent"])
    )


def clean_vehicle_master(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("Model_Year", F.col("Model_Year").cast("int"))
        .withColumn("Battery_Capacity_kWh", F.col("Battery_Capacity_kWh").cast("double"))
        .withColumn("Vehicle_Age_Years", F.col("Vehicle_Age_Years").cast("int"))
        .withColumn("Odometer_km", F.col("Odometer_km").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Model", "Region"])
    )


def clean_charging_sessions(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("Session_Start", F.to_timestamp("Session_Start", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("Session_End", F.to_timestamp("Session_End", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("Energy_Delivered_kWh", F.col("Energy_Delivered_kWh").cast("double"))
        .withColumn("Initial_SoC_Percent", F.col("Initial_SoC_Percent").cast("double"))
        .withColumn("Final_SoC_Percent", F.col("Final_SoC_Percent").cast("double"))
        .withColumn("Charging_Duration_Min", F.col("Charging_Duration_Min").cast("double"))
        .withColumn("Charging_Power_kW", F.col("Charging_Power_kW").cast("double"))
        .withColumn("Charging_Interruptions", F.col("Charging_Interruptions").cast("int"))
        .withColumn("Charger_Temperature_C", F.col("Charger_Temperature_C").cast("double"))
        .withColumn("Environment_Temperature_C", F.col("Environment_Temperature_C").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Session_Start", "Session_End"])
    )


def enrich_vehicle_data(telemetry_df: DataFrame, vehicle_master_df: DataFrame) -> DataFrame:
    return telemetry_df.join(vehicle_master_df, on="Vehicle_ID", how="left")


def compute_vehicle_summary(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("Vehicle_ID", "Model", "Region", "Vehicle_Age_Years")
        .agg(
            F.avg("SoC_Percent").alias("avg_battery_level"),
            F.avg("SoH_Percent").alias("avg_soh"),
            F.min("SoH_Percent").alias("min_soh"),
            F.max("SoH_Percent").alias("max_soh"),
            F.count("*").alias("telemetry_records"),
        )
    )
