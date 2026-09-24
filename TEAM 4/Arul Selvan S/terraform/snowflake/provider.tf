provider "snowflake" {
  account       = var.snowflake_account
  user          = var.snowflake_user
  password      = var.snowflake_password
  role          = var.snowflake_role
  authenticator = var.snowflake_authenticator

  experimental_features_enabled = [
    "PROVIDER_CONFIGURATION_ACCOUNT_FALLBACK"
  ]

  preview_features_enabled = [
    "snowflake_table_resource"
  ]
}