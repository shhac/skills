# Neutral Plan

Use this plan for `neutral` strength.

## Posture

Cover the passive issue-fit concerns first, then add a balanced code-quality pass. Neutral strength is more thorough than passive, but it is still primarily trying to decide whether the PR is a good, mergeable solution to the stated issue.

Call out meaningful maintainability, convention, naming, decomposition, and testability concerns when they materially improve the change. Do not hunt for every small nit.

## Load Lenses

Read these lens files:

- `lenses/issue-fit.md`
- `lenses/correctness-edge-cases.md`
- `lenses/structure-boundaries.md`
- `lenses/safety.md`
- `lenses/conventions.md`
- `lenses/naming.md`
- `lenses/function-decomposition.md`
- `lenses/complexity-shape.md`
- `lenses/testability-coverage.md`

## Applying Findings

- Prefer inline comments for specific, line-level issues.
- Prefer `suggestion` blocks for direct quick wins.
- Use `COMMENT` more readily than passive strength for material convention, maintainability, naming, decomposition, or test-quality concerns.
- Use `APPROVE` when the PR solves the issue and the concerns are minor or informational.
- Use `APPROVE` when the only remaining blocker is a failing or pending CI check that already blocks merge.
- Do not use `REQUEST_CHANGES` for ordinary quality concerns, even when the code is messy.
- Do not invent repo conventions. Infer them from nearby files, existing tests, docs, and patterns in the changed area.
- Do not demand a large rewrite when the PR is an acceptable incremental step. Name the better pattern as optional follow-up.

Keep the top-level `[AI Review][strength: neutral]` body focused on issue fit and the most important quality concerns. Put line-specific findings inline.
