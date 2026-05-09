# Analyst lenses

Phase 1 spawns one subagent per lens. Each subagent receives one section of this file verbatim — that section *is* its role. Pass each lens together with the scope and the standard fields from [conventions.md](conventions.md#subagent-conventions). Output uses the [Finding Record schema](conventions.md#finding-record-schema).

## 1. Function decomposition

Find functions that are too long or handle multiple concerns. Look for:

- Functions doing more than one thing (setup + logic + cleanup, fetch + transform + render).
- Functions hard to test because they mix side effects with pure logic.
- Opportunities to extract testable pure functions from effectful code.

## 2. File decomposition

Find files that are too large (350+ lines as a guideline, not a hard rule). Look for:

- Files containing multiple unrelated concepts.
- Files where one section could serve a broader audience (belongs in a shared/common location).
- Whether new files should be siblings, a subdirectory, or relocated to a shared space.
- Note: function decomposition (lens 1) may increase a file's function count, creating new file-split opportunities — flag these.

## 3. Complexity reduction

Find unnecessarily complex code. Look for:

- Deep nesting that could be flattened with early returns or guard clauses.
- `let x; try { x = ... } catch { ... }` patterns (or the equivalent in this language) that should be extracted into functions.
- Complex conditionals that could be simplified by inverting, decomposing, or using lookup tables.
- Overly clever code that sacrifices readability for brevity.

## 4. Pattern deduplication

Find repeated patterns that should be shared. Look for:

- Near-identical code blocks across files (not just exact duplicates — similar structure with minor variation).
- Repeated error handling, validation, or transformation patterns.
- Opportunities for shared utilities, but only when 3+ call sites exist — don't abstract prematurely.

## 5. Test coverage on critical paths

Identify critical code and assess its test coverage. Look for:

- Code that handles money, auth, data mutations, or external integrations.
- Edge cases that aren't covered (nulls, empty collections, boundary values, concurrent access).
- Functions that were recently decomposed (by lenses 1–3) and now need their own tests.
- If the project has no test infrastructure, still identify critical untested paths but note the gap.
