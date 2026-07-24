# Database Migrations Focus Pack

Load when changed files or PR context mention migrations, schema changes, indexes, constraints, backfills, data repair, data deletion, retention, or storage format changes. This pack covers operational databases: application migrations, live schema, and production data. For dbt or warehouse transformation-layer changes, use the dbt transformations and warehouse cost and performance packs instead.

Look for:

- Expand/contract rollout risks: application code using a new schema before migration is deployed, or migration dropping/renaming something old code still needs.
- Irreversible or hard-to-rollback changes without a clear plan.
- Backfills that are not idempotent, resumable, bounded, observable, or safe to retry.
- Locks, table rewrites, index build cost, long transactions, or migration ordering that can harm production availability.
- Data deletion or transformation without verification, auditability, or recovery path.
- Schema defaults/nullability/constraints that break existing rows or older writers.
- Irreversible destructive DDL (DROP TABLE/COLUMN, TRUNCATE, data deletion) in a PR whose safety depends on other PRs or systems landing first. This is a `⚠️ P1` review finding, not a merge-gate/ops concern: verify the prerequisites are landed (merged, deployed where checkable) or recommend splitting the destructive migration into its own PR that merges last.
- Declared schema, index, or constraint changes that are never wired into the deploy or migration path, so they silently no-op — for example an index defined on a model but never created on deploy, a migration file never registered with the runner, or a constraint added in code but not applied to the live schema. Trace the declared change to the code path that actually executes it.

Good findings state the deploy ordering or data safety risk, identify the affected readers/writers, and suggest the smallest safer direction: split expand/contract steps, add compatibility code, make backfills resumable, add guards/verification, or document rollback/operational steps.

Reference basis: evolutionary database design patterns and general production migration practice.
