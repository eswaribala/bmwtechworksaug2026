# Product Requirements Document

## Objective
Provide BMW leadership with one trusted view of commercial performance and vehicle health.

## Users
Executives need headline KPIs and trends. Regional managers need drill-down to dealers and models limited to their region. Data/platform owners need quality, freshness, and failure visibility.

## Functional requirements

1. Ingest six source domains: vehicle master, telemetry, sales, dealer, maintenance, and warranty.
2. Validate nulls, duplicate keys, referential integrity, dates, battery range 0-100, and temperature range -50 to 150 C.
3. Preserve invalid rows in a rejected zone with reason and source metadata.
4. Expose repeatable Athena tables and KPI queries.
5. Present seven KPI cards, eight requested visuals, four filters, and BMW > region > dealer > model drilldown.
6. Enforce regional RLS for South, North, East, and West managers.
7. Log processing and publish CloudWatch metrics.

## Non-functional requirements

- No secrets in Git; use IAM roles and GitHub OIDC.
- S3 encryption, versioning, TLS-only access, least privilege.
- Repeatable deployment through Terraform and GitHub Actions.
- Unit test KPI formulas and validation rules; target at least 80% Python coverage.
- Dashboard refresh SLA: daily by 06:00 local time, with freshness shown to users.

## Acceptance criteria

A representative source load produces valid curated data and rejected rows. Athena KPI results reconcile to independent Python calculations. QuickSight shows the same totals, filters correctly by date/region/model/dealer, and each manager cannot view another region. CI blocks a merge on lint or test failure. CloudWatch alerts on job failure, stale data, or validation rate above threshold.

## Out of scope

Predictive maintenance, real-time streaming, customer PII enrichment, and Snowflake are optional extensions rather than MVP deliverables.
