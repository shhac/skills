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

Good objections are specific enough that the author can respond with a fix, a test, or a clear explanation. Avoid vague "this feels risky" objections unless you can name the risk.
