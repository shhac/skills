# Failure Modes and Scale Lens

Ask: "Where would this fall over?"

Use this lens as a lightweight failure-mode sweep. It complements the correctness lens by looking past the immediate happy path into volume, timing, dependency, and operational edges.

Look for:

- Inputs, collections, payloads, or traffic volumes larger than the changed code appears to assume
- Empty, duplicate, out-of-order, stale, partial, malformed, or mixed-version data
- Slow, unavailable, inconsistent, or rate-limited dependencies
- Retry, rerun, rollback, timeout, cancellation, and idempotency behavior
- Unbounded loops, memory growth, query fan-out, N+1 work, large payloads, or lock contention
- Race conditions, concurrent writes, reordered events, and repeated delivery
- Partial success, partial failure, recovery, fallback, and user-visible degradation paths
- Operational visibility when the edge occurs: logs, metrics, error messages, alerts, or audit trails
- Deploy or migration windows where old and new code, schemas, clients, workers, caches, or persisted data coexist

Good findings name the concrete scenario, explain why the current change would fall over, estimate severity using the skill's global P0-P4 scale, and suggest the smallest guard, fallback, bound, retry/idempotency change, partial-success handling, or observability improvement.

Make a scale concern `⚠️ P1` only when the concrete scenario likely breaks issue fit, correctness, safety, or a runtime contract. Otherwise use `🔧 P2`, `ℹ️ FYI`, or omit it depending on the loaded profile.
