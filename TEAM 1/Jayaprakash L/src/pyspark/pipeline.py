from pathlib import Path
from .spark_session import create_spark
from .transform import transform_telemetry
from .aggregations import (
    vehicle_efficiency, model_efficiency,
    region_efficiency, range_trend
)
from .ranking import top_vehicles, bottom_vehicles

def run(input_csv, output_dir):
    spark = create_spark()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(input_csv)
    )

    df = transform_telemetry(df)
    df.cache()

    vehicle = vehicle_efficiency(df)
    model = model_efficiency(df)
    region = region_efficiency(df)
    trend = range_trend(df)
    top = top_vehicles(vehicle, 5)
    bottom = bottom_vehicles(vehicle, 5)

    vehicle.write.mode("overwrite").parquet(str(out/"vehicle_efficiency"))
    model.write.mode("overwrite").parquet(str(out/"model_efficiency"))
    region.write.mode("overwrite").parquet(str(out/"region_efficiency"))
    trend.write.mode("overwrite").parquet(str(out/"range_trend"))
    top.write.mode("overwrite").parquet(str(out/"top_vehicles"))
    bottom.write.mode("overwrite").parquet(str(out/"bottom_vehicles"))

    df.unpersist()
    spark.stop()

if __name__ == "__main__":
    run("data/dataset.csv", "data/curated")
