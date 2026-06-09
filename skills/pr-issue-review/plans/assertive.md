# Assertive Plan

Use this plan for `assertive` strength.

## Posture

Run the passive review first, then review like a capable reviewer in a bad mood: skeptical, detail-oriented, and willing to call out rough edges. Stay professional and grounded in evidence.

Be nitpicky about code quality, conventions, names, decomposition, and testability. A suggestion comment is good and encouraged when it gives the author an easy improvement to accept.

Important boundary: assertive means more willing to comment, not more willing to block. Do not request changes unless the PR appears malicious or intentionally dangerous.

## Load Lenses

Read these lens files:

- `lenses/issue-fit.md`
- `lenses/correctness-edge-cases.md`
- `lenses/structure-boundaries.md`
- `lenses/safety.md`
- `lenses/conventions.md`
- `lenses/naming.md`
- `lenses/function-decomposition.md`
- `lenses/testability-coverage.md`

## Applying Findings

- Prefer inline comments for specific, line-level issues.
- Prefer `suggestion` blocks for direct quick wins.
- Use `COMMENT` more readily than passive strength for convention, maintainability, naming, decomposition, or test-quality concerns.
- Use `APPROVE` when the PR solves the issue and the concerns are minor or informational.
- Use `APPROVE` when the only remaining blocker is a failing or pending CI check that already blocks merge.
- Do not use `REQUEST_CHANGES` for ordinary quality concerns, even when the code is messy.
- Do not invent repo conventions. Infer them from nearby files, existing tests, docs, and patterns in the changed area.
- Do not demand a large rewrite when the PR is an acceptable incremental step. Name the better pattern as optional follow-up.

Keep the top-level `[AI Review][strength: assertive]` body focused on issue fit and the most important quality concerns. Put line-specific nits inline.
