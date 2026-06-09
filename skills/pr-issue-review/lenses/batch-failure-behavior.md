# Batch Failure Behavior Lens

Use this lens when the PR adds or changes batch operations, fan-out requests, retries, background jobs, bulk UI actions, parallel work, queues, migrations, or multi-item writes.

Look for:

- All-or-nothing behavior where partial success is expected or safer
- One item failure preventing unrelated items from completing
- Success/failure counts that do not match attempted, skipped, failed, and completed work
- Error handling that loses per-item context or reports a misleading success/result
- Retrying, cancellation, stale input, idempotency, or duplicate-submit risks
- Read/write paths with different failure semantics

Good findings explain the failure mode, who sees the bad result, and the direction: per-item error handling, settled-result collection, structured results, separate skipped counts, idempotency guards, or clearer partial-failure messaging.
