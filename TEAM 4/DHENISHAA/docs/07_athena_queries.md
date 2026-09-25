# 07. Athena Queries

Athena runs SQL against data in the Glue Data Catalog.

## Example query patterns
- total vehicles
- total telemetry events
- average battery level
- average temperature by region
- fault distribution
- revenue by model

## Best practices
- Use partition columns in WHERE clauses.
- Avoid SELECT *.
- Filter early to reduce scan size.
- Use aggregated queries for dashboards.
