# Final Presentation and Demo Script

## 10-minute flow

**Minute 0-1: Problem.** BMW leadership lacks a consolidated view across commercial results, fleet health, service, faults, and warranty cost. Decisions are slowed by disconnected files.

**Minute 1-2: Architecture.** Walk from CSV and S3 raw through Python quality gates, curated Parquet, Athena, QuickSight, and CloudWatch. Call out rejected-row isolation and least privilege.

**Minute 2-4: Pipeline.** Show one input file, a validation result, a rejected example, the curated partition, and the Athena query result. Explain partitioning and reconciliation.

**Minute 4-8: Dashboard.** Start with KPI cards. Filter to South, select a date range, drill BMW > South > dealer > model, inspect revenue and warranty trends, then show fault and battery context. Switch to a South manager account and demonstrate that North data is hidden.

**Minute 8-9: Trust.** Show pytest output, GitHub Actions checks, CloudWatch metrics/logs, and a freshness timestamp.

**Minute 9-10: Benefit.** Leadership gets one governed view, faster regional comparison, earlier visibility of vehicle-health risk, and a repeatable foundation for predictive analytics.

## Close with

MVP limitations are batch refresh and descriptive analytics. The next value step is anomaly detection and predictive maintenance once data history and labels are mature.
