# Operations and Monitoring

## CloudWatch metrics

Namespace `BMW/ExecutiveAnalytics`: `RecordsProcessed`, `ValidationFailures`, `ProcessingFailures`, `ExecutionDurationMs`, `FilesProcessed`, and `DataFreshnessHours`. Add dimensions `Dataset` and `Environment`.

## Alarms

Alarm if `ProcessingFailures >= 1` per run, validation failure rate exceeds 5%, execution duration exceeds the baseline p95 by 25%, or freshness exceeds 30 hours. Route alarms to an SNS topic owned by the platform support group.

## Logs

Structured JSON logs include `run_id`, `dataset`, `source_key`, `records_in`, `records_out`, `records_rejected`, `duration_ms`, and `error_type`. Never log credentials, full VINs, customer IDs, or raw payloads.

## Runbook

1. Check the failed run's CloudWatch `run_id` and source object.
2. Check schema errors before row-level errors.
3. Inspect rejected counts and sample reasons.
4. Correct or quarantine the source file; do not manually edit curated data.
5. Re-run the same partition with an idempotency key.
6. Validate Athena row counts and dashboard freshness.
7. Record incident cause and corrective action.
