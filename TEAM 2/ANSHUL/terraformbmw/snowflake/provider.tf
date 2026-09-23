terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 2.20"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "snowflake" {
  organization_name        = var.snowflake_organization
  account_name             = var.snowflake_account
  user                     = var.snowflake_user
  password                 = var.snowflake_password
  role                     = "ACCOUNTADMIN"
  preview_features_enabled = ["snowflake_table_resource"]
}