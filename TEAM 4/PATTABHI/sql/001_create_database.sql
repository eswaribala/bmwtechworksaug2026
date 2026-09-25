CREATE DATABASE IF NOT EXISTS bmw_analytics
COMMENT 'BMW Executive Analytics database'
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/athena/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.vehicle_master (
  vehicle_id string, vin string, model string, model_year int, fuel_type string,
  region string, manufacturing_date date
)
PARTITIONED BY (ingestion_date date)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'skip.header.line.count' = '1')
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/processed/vehicle/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.vehicle_telemetry (
  event_id string, vehicle_id string, event_timestamp timestamp, speed double,
  battery_level double, temperature double, odometer double, latitude double,
  longitude double, fault_code string
)
PARTITIONED BY (event_date date)
STORED AS PARQUET
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/curated/telemetry/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.dealer (
  dealer_id string, dealer_name string, city string, region string,
  capacity int, rating double
)
STORED AS PARQUET
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/curated/dealer/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.sales (
  sale_id string, vehicle_id string, dealer_id string, customer_id string,
  sale_date date, model string, region string, price decimal(18,2), quantity int,
  revenue decimal(20,2)
)
PARTITIONED BY (sale_month string)
STORED AS PARQUET
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/curated/sales/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.maintenance (
  service_id string, vehicle_id string, dealer_id string, service_date date,
  service_type string, odometer double, parts_cost decimal(18,2),
  labour_cost decimal(18,2), failure_code string, service_cost decimal(18,2)
)
PARTITIONED BY (service_month string)
STORED AS PARQUET
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/curated/maintenance/';

CREATE EXTERNAL TABLE IF NOT EXISTS bmw_analytics.warranty (
  claim_id string, vehicle_id string, claim_date date, component string,
  claim_amount decimal(18,2), claim_status string
)
PARTITIONED BY (claim_month string)
STORED AS PARQUET
LOCATION 's3://bmw-executive-analytics-dashboard-pattabhi/curated/warranty/';
