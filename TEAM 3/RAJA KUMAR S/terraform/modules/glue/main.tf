/**
 * Glue Module — AWS Glue Data Catalog
 * Creates the Glue database and tables for BMW curated datasets.
 *
 * Spec §18: "AWS Glue Data Catalog stores metadata about curated datasets."
 *
 * Tables registered:
 *   bmw_data_quality.vehicle_master  → s3://<bucket>/curated/vehicle_master/
 *   bmw_data_quality.telemetry       → s3://<bucket>/curated/telemetry/
 *   bmw_data_quality.data_quality_report → s3://<bucket>/reports/
 */

# ────────────────────────────────────────────────
# Glue Database
# ────────────────────────────────────────────────

resource "aws_glue_catalog_database" "bmw" {
  name        = "bmw_data_quality"
  description = "BMW Data Quality Platform — curated datasets (Participant 12)"

  location_uri = "s3://${var.bucket_name}/curated/"
}

# ────────────────────────────────────────────────
# Table: vehicle_master
# ────────────────────────────────────────────────

resource "aws_glue_catalog_table" "vehicle_master" {
  name          = "vehicle_master"
  database_name = aws_glue_catalog_database.bmw.name
  description   = "BMW vehicle master reference — curated validated records"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification"  = "csv"
    "delimiter"       = ","
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location      = "s3://${var.bucket_name}/curated/vehicle_master/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
      parameters = {
        "field.delim"            = ","
        "skip.header.line.count" = "1"
      }
    }

    columns {
      name    = "vehicle_id"
      type    = "string"
      comment = "Unique vehicle identifier"
    }
    columns {
      name    = "vin"
      type    = "string"
      comment = "Vehicle Identification Number (17 chars)"
    }
    columns {
      name    = "model"
      type    = "string"
      comment = "BMW model name"
    }
    columns {
      name    = "model_year"
      type    = "int"
      comment = "Year of manufacture"
    }
    columns {
      name    = "region"
      type    = "string"
      comment = "Sales region"
    }
    columns {
      name    = "color"
      type    = "string"
      comment = "Vehicle color"
    }
  }
}

# ────────────────────────────────────────────────
# Table: telemetry
# ────────────────────────────────────────────────

resource "aws_glue_catalog_table" "telemetry" {
  name          = "telemetry"
  database_name = aws_glue_catalog_database.bmw.name
  description   = "BMW telemetry events — curated validated records"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification"  = "csv"
    "delimiter"       = ","
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location      = "s3://${var.bucket_name}/curated/telemetry/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
      parameters = {
        "field.delim"            = ","
        "skip.header.line.count" = "1"
      }
    }

    columns {
      name    = "event_id"
      type    = "string"
      comment = "Unique telemetry event ID"
    }
    columns {
      name    = "vehicle_id"
      type    = "string"
      comment = "Vehicle reference (FK to vehicle_master)"
    }
    columns {
      name    = "vin"
      type    = "string"
      comment = "Vehicle Identification Number"
    }
    columns {
      name    = "timestamp"
      type    = "timestamp"
      comment = "Event timestamp"
    }
    columns {
      name    = "battery_level"
      type    = "double"
      comment = "Battery level 0–100"
    }
    columns {
      name    = "speed_kmh"
      type    = "double"
      comment = "Vehicle speed in km/h"
    }
    columns {
      name    = "temperature_c"
      type    = "double"
      comment = "Ambient temperature in Celsius"
    }
    columns {
      name    = "latitude"
      type    = "double"
      comment = "GPS latitude"
    }
    columns {
      name    = "longitude"
      type    = "double"
      comment = "GPS longitude"
    }
  }
}

# ────────────────────────────────────────────────
# Table: data_quality_report
# ────────────────────────────────────────────────

resource "aws_glue_catalog_table" "data_quality_report" {
  name          = "data_quality_report"
  database_name = aws_glue_catalog_database.bmw.name
  description   = "BMW data quality pipeline reports (0–100 score)"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "json"
  }

  storage_descriptor {
    # Scoped to reports/summary/ (not the whole reports/ tree) so the table
    # only scans flat run summaries — excludes reports/athena-results/,
    # reports/<dataset>/*_quality_report.*, and reports/_history.json.
    location      = "s3://${var.bucket_name}/reports/summary/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
      parameters = {
        "serialization.format" = "1"
      }
    }

    columns {
      name    = "dataset_name"
      type    = "string"
      comment = "Name of the dataset that was validated"
    }
    columns {
      name    = "execution_timestamp"
      type    = "string"
      comment = "When the pipeline ran"
    }
    columns {
      name    = "total_records"
      type    = "int"
      comment = "Total rows in dataset"
    }
    columns {
      name    = "valid_records"
      type    = "int"
      comment = "Records passing all quality checks"
    }
    columns {
      name    = "rejected_records"
      type    = "int"
      comment = "Records failing one or more checks"
    }
    columns {
      name    = "quality_score"
      type    = "double"
      comment = "Data quality score 0–100"
    }
    columns {
      name    = "null_issues"
      type    = "int"
      comment = "Count of null violations"
    }
    columns {
      name    = "duplicate_records"
      type    = "int"
      comment = "Count of duplicate records"
    }
    columns {
      name    = "invalid_vin_count"
      type    = "int"
      comment = "Count of invalid VINs"
    }
    columns {
      name    = "invalid_date_count"
      type    = "int"
      comment = "Count of invalid dates"
    }
    columns {
      name    = "range_violation_count"
      type    = "int"
      comment = "Count of out-of-range values"
    }
    columns {
      name    = "referential_errors"
      type    = "int"
      comment = "Count of referential integrity violations"
    }
  }
}
