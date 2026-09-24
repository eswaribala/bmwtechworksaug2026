# QuickSight Setup

QuickSight uses the Athena view for this project.

## Athena option

Run [sql/athena_setup.sql](sql/athena_setup.sql) in the Athena Query Editor,
then create the dataset as follows:

1. Open Amazon QuickSight.
2. Select **Datasets** and **New dataset**.
3. Select **Athena**.
4. Select data source `AwsDataCatalog`.
5. Select database `ev_battery_health`.
6. Select view `vehicle_health_dashboard`.
7. Choose **Import to SPICE**.
8. Select **Visualize**.

QuickSight must have permission to use Athena and read the S3 locations
`s3://ev-battery-health-data/curated/vehicle_health/` and
`s3://ev-battery-health-data/athena-results/`.

Use SPICE for this small vehicle-level summary.

## 3. Recommended visuals

Create these visuals from `vehicle_health_dashboard`:

| Visual | Group/dimension | Measure or filter |
|---|---|---|
| Health distribution | `BATTERY_HEALTH_CATEGORY` | Count of `VEHICLE_ID` |
| Average SoH by model | `MODEL` | Average of `AVG_SOH` |
| Risk by region | `REGION` | Count of `VEHICLE_ID`, filter Critical |
| SoH vs charging | `CHARGING_FREQUENCY` | Average `AVG_SOH`, color by category |
| Risk table | `VEHICLE_ID`, `MODEL`, `REGION` | `AVG_SOH`, `SOH_DROP`, `HEALTH_SCORE` |

Add controls for:

- `BATTERY_HEALTH_CATEGORY`
- `MODEL`
- `REGION`
- `VEHICLE_AGE_YEARS`

Sort the risk table by `AVG_SOH` ascending and filter it to `Watch` and `Critical` when reviewing vehicles needing attention.

## Refresh after each pipeline run

After the PySpark job writes new Parquet files:

1. Run `MSCK REPAIR TABLE ev_battery_health.vehicle_health` in Athena.
2. In QuickSight, open the dataset.
3. Select **Refresh now** for the SPICE dataset.

This makes newly written health-category partitions visible before QuickSight
refreshes SPICE.
