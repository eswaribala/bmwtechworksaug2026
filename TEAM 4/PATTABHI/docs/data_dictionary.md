# Data Dictionary

| Domain | Column | Type | Rule |
|---|---|---|---|
| vehicle_master | vehicle_id | string | Required unique business key |
| vehicle_master | vin | string | Required VIN; unique where available |
| vehicle_master | model | string | Required model |
| vehicle_master | model_year | int | Four-digit year |
| vehicle_master | fuel_type | string | Controlled value |
| vehicle_master | region | string | North, South, East, or West |
| vehicle_master | manufacturing_date | date | Valid ISO date |
| telemetry | event_id | string | Required unique event key |
| telemetry | vehicle_id | string | Must exist in vehicle master |
| telemetry | timestamp | timestamp | Valid event timestamp |
| telemetry | speed | double | Non-negative |
| telemetry | battery_level | double | 0 through 100 percent |
| telemetry | temperature | double | -50 through 150 C |
| telemetry | odometer | double | Non-negative and non-decreasing per vehicle |
| telemetry | fault_code | string | Nullable; non-null counts as critical fault |
| sales | sale_id | string | Required unique sale key |
| sales | vehicle_id | string | Must exist in vehicle master |
| sales | dealer_id | string | Dealer reference |
| sales | sale_date | date | Valid date |
| sales | price | decimal | Non-negative unit price |
| sales | quantity | int | Positive quantity |
| maintenance | service_id | string | Required unique service key |
| maintenance | parts_cost/labour_cost | decimal | Non-negative; summed to service_cost |
| warranty | claim_id | string | Required unique claim key |
| warranty | claim_amount | decimal | Non-negative amount |
| warranty | claim_status | string | Open, Approved, Rejected, Paid |

## Derived fields

`revenue = price * quantity`; `service_cost = parts_cost + labour_cost`; `sale_month`, `service_month`, and `claim_month` are partition keys. `event_date` is derived from telemetry timestamp.
