# Passive Plan

Use this plan for `passive` strength.

## Posture

Be focused, restrained, and issue-oriented. The review asks whether the PR solves the stated issue without turning into a general cleanup pass.

Surface only concerns that affect issue fit, correctness, safety, or clearly relevant maintainability. Avoid style nits, speculative rewrites, and broad best-practice commentary.

## Load Lenses

Read these lens files, and no assertive-only lenses:

- `lenses/issue-fit.md`
- `lenses/correctness-edge-cases.md`
- `lenses/structure-boundaries.md`
- `lenses/safety.md`

## Applying Findings

- Prefer `APPROVE` when the PR appears to solve the stated issue.
- Use `COMMENT` when issue fit is incomplete, ambiguous, or cannot be verified.
- Leave inline comments only for concrete, line-specific findings that materially affect the review.
- Use `suggestion` blocks for small quick wins when useful, but do not hunt for nits.
- Do not request changes unless the PR appears malicious or intentionally dangerous.

Keep the top-level `[AI Review][strength: passive]` body short: state whether the PR solves the issue, why, what context was checked, and any limitations.
