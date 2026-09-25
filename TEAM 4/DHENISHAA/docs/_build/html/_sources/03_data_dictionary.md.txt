# 03. Data Dictionary

## Vehicle master
- vehicle_id: unique vehicle identifier
- vin: vehicle identification number
- model: vehicle model name
- model_year: manufacturing year
- region: geographic region
- dealer_id: dealer or service partner ID
- battery_capacity_kwh: battery capacity in kWh
- manufacture_date: manufacturing date

## Telemetry
- vehicle_id
- event_timestamp
- event_date
- year
- month
- region
- speed_kmh
- battery_level
- battery_temperature
- engine_temperature
- latitude
- longitude
- fault_code

## Sales
- sale_id
- vehicle_id
- dealer_id
- model
- region
- sale_date
- sale_amount

## Maintenance
- maintenance_id
- vehicle_id
- service_date
- service_type
- repair_cost
- dealer_id

## Warranty
- claim_id
- vehicle_id
- component
- claim_date
- claim_amount
- dealer_id
