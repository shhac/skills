# Database Migrations Focus Pack

Load when changed files or PR context mention migrations, schema changes, indexes, constraints, backfills, data repair, data deletion, retention, or storage format changes.

Look for:

- Expand/contract rollout risks: application code using a new schema before migration is deployed, or migration dropping/renaming something old code still needs.
- Irreversible or hard-to-rollback changes without a clear plan.
- Backfills that are not idempotent, resumable, bounded, observable, or safe to retry.
- Locks, table rewrites, index build cost, long transactions, or migration ordering that can harm production availability.
- Data deletion or transformation without verification, auditability, or recovery path.
- Schema defaults/nullability/constraints that break existing rows or older writers.

Good findings state the deploy ordering or data safety risk, identify the affected readers/writers, and suggest the smallest safer direction: split expand/contract steps, add compatibility code, make backfills resumable, add guards/verification, or document rollback/operational steps.

Reference basis: evolutionary database design patterns and general production migration practice.
