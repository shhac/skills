# Correctness And Edge Cases Lens

Look for behavior that could make the PR fail to solve the issue or regress adjacent behavior.

Check:

- Logic errors, off-by-one mistakes, race conditions, ordering bugs, or stale state
- Missing null, empty, duplicate, permission, concurrency, retry, timeout, or partial-failure handling
- Input validation and output shape at system boundaries
- Backwards compatibility for callers, persisted data, APIs, and user workflows
- Whether changed tests cover the important edge cases rather than only the happy path

For every changed write path, walk one explicit read-modify-write trace: what was read, how stale can it be by write time, and what enforces the assumption at the write (compare-and-set, version, unique index, transaction)? A check-then-act on state that another actor can change in between is a finding even when each half is individually correct.

For every changed loop whose exit depends on input data: name the termination condition and what bounds it under duplicate, unknown, or reordered elements.

Focus on concrete failure modes visible from the diff and nearby code.
