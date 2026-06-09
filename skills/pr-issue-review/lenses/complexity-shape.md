# Complexity Shape Lens

Check whether the changed code has a maintainable shape.

Use length and return-count signals as heuristics, not hard rules. Prefer comments that explain the readability or testability problem created by the shape.

Look for:

- Functions that are long enough to require holding too much state in mind
- Files that are becoming dumping grounds for unrelated behavior
- Functions with several non-trivial return paths that encode different business rules
- Guard clauses that improve clarity versus returns that fragment the story
- Large test cases or fixtures where important behavior is hard to find
- Dense branches where named helpers or intermediate values would expose intent
- Added code that makes the changed area harder to review than the surrounding code

Good findings explain why the shape matters: hidden responsibilities, unclear control flow, fragile tests, hard-to-name chunks, or behavior that should be isolated for reuse or direct testing.

Do not flag length alone. A long table-driven test, schema, mapping, or declarative config may be fine if it is cohesive and easy to scan.
