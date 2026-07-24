# Aggressive Objections Lens

This lens is intentionally skeptical. Use it only from the aggressive profile.

Try to disprove that the PR is ready to approve.

Look for:

- The PR solves the happy path but misses stated acceptance criteria or linked context
- The change relies on assumptions that are not enforced by types, validation, permissions, or tests
- Tests prove the implementation detail but not the behavior users or callers depend on
- A partial stack slice claims more than it actually delivers
- The implementation creates a future migration, data repair, operational, or rollback problem
- The change makes a bug less visible rather than fixing the underlying issue
- The diff introduces broad coupling, hidden side effects, or confusing ownership boundaries
- The PR appears correct only because an adjacent failure mode was not inspected
- The PR removes, excludes, or disables something (a field, a validation, a gate, a migration step): trace what stops happening downstream and who depended on it. When removal is the stated goal, name the cost anyway — "excluding these fields also stops these questions being captured" is a finding even when exclusion fixes the incident
- The PR is an emergency or incident fix: state explicitly what the fix trades away versus a root-cause fix, so the human merging it is choosing the tradeoff knowingly

Good objections are specific enough that the author can respond with a fix, a test, or a clear explanation. Avoid vague "this feels risky" objections unless you can name the risk.
