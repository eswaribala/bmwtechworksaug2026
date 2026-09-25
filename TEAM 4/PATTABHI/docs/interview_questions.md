# Interview Questions and Answers

**Why S3 plus Athena?** S3 provides durable, low-cost layered storage; Athena queries it serverlessly without managing a warehouse. Parquet and partitions control scan cost.

**Why reject rows instead of failing every file?** Row-level issues should not discard valid business data. File-level schema failures still fail fast because they make interpretation unsafe.

**How do you prevent duplicate revenue?** Keep each fact at its source grain, aggregate before joining, use distinct service/event keys, and reconcile Python totals to Athena. Avoid joining multiple one-to-many facts in a single KPI query.

**How is RLS implemented?** QuickSight dataset rules map identity to region; managers receive only their region, while executive access is a separate controlled group.

**How are secrets handled?** GitHub OIDC assumes an AWS role; local development uses the AWS credential provider chain or environment variables. No static keys are committed.

**How would you scale this?** Catalog schemas and partitions with Glue, use Glue or ECS for larger batches, add Lake Formation governance, and move high-concurrency workloads to a warehouse only when justified.

**What would you monitor?** Counts, rejection rates, failures, duration, freshness, Athena scan cost, and QuickSight refresh status.

**What is the biggest data risk?** Grain mismatch across telemetry, sales, maintenance, and warranty can multiply values. The design keeps facts separate and uses conformed dimensions for analysis.
