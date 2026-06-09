# Correctness And Edge Cases Lens

Look for behavior that could make the PR fail to solve the issue or regress adjacent behavior.

Check:

- Logic errors, off-by-one mistakes, race conditions, ordering bugs, or stale state
- Missing null, empty, duplicate, permission, concurrency, retry, timeout, or partial-failure handling
- Input validation and output shape at system boundaries
- Backwards compatibility for callers, persisted data, APIs, and user workflows
- Whether changed tests cover the important edge cases rather than only the happy path

Focus on concrete failure modes visible from the diff and nearby code.
