# S3 storage layout:
# s3://<bucket-name>/processed/maintenance_cleaned.csv
# s3://<bucket-name>/processed/maintenance_dealer_joined.csv
# s3://<bucket-name>/athena-results/   <-- Athena query results are written here

# The actual bucket and uploaded objects are defined in main.tf.
# Keeping this file intentionally minimal avoids duplicate S3 resources.
