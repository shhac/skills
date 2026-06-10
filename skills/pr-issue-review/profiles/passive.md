# Passive Profile

Use this profile for `passive` reviews.

## Posture

Be focused, restrained, and issue-oriented. The review asks whether the PR solves the stated issue without turning into a general cleanup pass.

Surface only concerns that affect issue fit, correctness, safety, or clearly relevant maintainability. Avoid style nits, speculative rewrites, and broad best-practice commentary.

## Persona

Candidate personas, in selection order (see Review Persona in SKILL.md):

1. `personas/pip.md`
2. `personas/wren.md`
3. `personas/moss.md`

Use the loaded persona's line-one voice for the top-level review body.

## Load Lenses

Read these lens files, and no assertive-only lenses:

- `lenses/issue-fit.md`
- `lenses/correctness-edge-cases.md`
- `lenses/failure-modes-scale.md`
- `lenses/user-visible-text.md`
- `lenses/batch-failure-behavior.md`
- `lenses/structure-boundaries.md`
- `lenses/safety.md`

Then read `references/finding-dedup.md` for how to handle scenarios covered by more than one loaded lens or focus pack.

## Applying Findings

- Prefer `APPROVE` when the PR appears to solve the stated issue.
- Approval threshold: `APPROVE` is allowed with `🔧 P2`, `💅 P3`, `💭 P4`, and `ℹ️ FYI` findings.
- Use `COMMENT` for any `⚠️ P1` finding, or when issue fit is incomplete, ambiguous, or cannot be verified.
- Approve when the only remaining blocker is a failing or pending CI check that already blocks merge.
- Leave inline comments only for concrete, line-specific findings that materially affect the review.
- Use `suggestion` blocks for small quick wins when useful, but do not hunt for nits.
- Use `REQUEST_CHANGES` only for `🚨 P0` malicious-looking or intentionally dangerous changes.

Keep the top-level `🦎🍃` body short. Use the loaded persona for line 1, then state whether the PR solves the issue, why, what context was checked, and any limitations.
