# Function Decomposition Lens

Check whether changed functions and methods are decomposed at a useful level.

Look for:

- Functions doing multiple unrelated jobs
- Deep nesting, long conditional chains, or mixed validation/transformation/side-effect logic
- Repeated blocks that should be extracted or consolidated
- Helper functions that are too small, too indirect, or hide simple logic
- New abstractions that make call sites harder to read

Prefer decomposition that improves readability, testability, or reuse. Do not recommend splitting merely because a function is long.
