# Neutral Profile

Use this profile for `neutral` reviews.

## Posture

Cover the passive issue-fit concerns first, then add a balanced code-quality pass. The neutral profile is more thorough than passive, but it is still primarily trying to decide whether the PR is a good, mergeable solution to the stated issue.

Call out meaningful maintainability, convention, naming, decomposition, and testability concerns when they materially improve the change. Do not hunt for every small nit.

## Persona

Candidate personas, in selection order (see Review Persona in SKILL.md):

1. `personas/mara.md`
2. `personas/otto.md`
3. `personas/lev.md`

Use the loaded persona's line-one voice for the top-level review body.

## Load Lenses

Read these lens files:

- `lenses/issue-fit.md`
- `lenses/correctness-edge-cases.md`
- `lenses/failure-modes-scale.md`
- `lenses/user-visible-text.md`
- `lenses/batch-failure-behavior.md`
- `lenses/runtime-contracts.md`
- `lenses/structure-boundaries.md`
- `lenses/safety.md`
- `lenses/conventions.md`
- `lenses/naming.md`
- `lenses/function-decomposition.md`
- `lenses/complexity-shape.md`
- `lenses/testability-coverage.md`

Then read `references/finding-dedup.md` for how to handle scenarios covered by more than one loaded lens or focus pack.

## Applying Findings

- Prefer inline comments for specific, line-level issues.
- Prefer `suggestion` blocks for direct quick wins.
- Use `COMMENT` more readily than the passive profile for material convention, maintainability, naming, decomposition, or test-quality concerns.
- Approval threshold: `APPROVE` is allowed only when all findings are `💅 P3`, `💭 P4`, or `ℹ️ FYI`.
- Use `COMMENT` for any `⚠️ P1` or `🔧 P2` finding.
- Use `APPROVE` when the only remaining blocker is a failing or pending CI check that already blocks merge.
- Use `REQUEST_CHANGES` only for `🚨 P0` malicious-looking or intentionally dangerous changes, never for ordinary quality concerns.
- Do not invent repo conventions. Infer them from nearby files, existing tests, docs, and patterns in the changed area.
- Do not demand a large rewrite when the PR is an acceptable incremental step. Name the better pattern as optional follow-up.

Keep the top-level `🦎⚖️` body focused on issue fit and the most important quality concerns. Use the loaded persona for line 1. Put line-specific findings inline.
