# Examples

Three worked examples covering the most common branches through this skill.

---

## Example 1 — Settle in three iterations

**User request:** `/repeat-until-settled improve-code-structure then release`

**Setup.** Orchestrator records `START_SHA = e4a1c9f` and `START_TREE_HASH = sha256(<empty diff>)` (clean working tree). `FINGERPRINTS = []`, `iteration = 0`, `consecutive_stalls = 0`.

**Iteration 1.**
- pre = `(e4a1c9f, <empty>)`
- Invokes `improve-code-structure`. Inner skill analyzes, presents 8 recommendations, user approves all. Phase 2 lands them, Phase 3 cleans up 2 dead exports, Phase 4 reports.
- post = `(7b2d04a, <empty>)` — committed
- Outcome: **Continuing** (post != pre, not a cycle).
- `FINGERPRINTS = [(7b2d04a, <empty>)]`.

**Iteration 2.**
- pre = `(7b2d04a, <empty>)`
- Inner skill runs again. Finds 3 new recommendations that emerged from iteration 1's restructuring (files that are now ripe for further splitting). User approves 2. Phase 3 finds 1 dead utility introduced by the refactor.
- post = `(c19fe87, <empty>)`
- Outcome: **Continuing**.
- `FINGERPRINTS = [(7b2d04a, <empty>), (c19fe87, <empty>)]`.

**Iteration 3.**
- pre = `(c19fe87, <empty>)`
- Inner skill analyzes. Phase 1 returns no recommendations — the codebase is well-structured at this point. Phase 2 has nothing to do. Phase 3 is skipped (no Phase 2 changes). Phase 4 summary: "Analysis complete. No recommendations."
- post = `(c19fe87, <empty>)`
- Outcome: **Settled** — git delta is zero AND the inner skill explicitly reported no recommendations.

**Convergence summary:**

```
## Convergence summary

- Iterations: 3
- Exit reason: settled
- Net change since start: 11 files changed, +318/-247 lines
- Notable events: none

## Iteration log

| # | Outcome    | Net change                                        |
|---|------------|---------------------------------------------------|
| 1 | continuing | 8 refactors landed, 2 dead exports cleaned up    |
| 2 | continuing | 2 follow-on refactors landed, 1 dead util gone  |
| 3 | settled    | (no change — inner skill reported no findings)  |
```

**Follow-up.** The orchestrator invokes `/release` as if the user had just typed it.

---

## Example 2 — Cycle resolved autonomously

**User request:** `/repeat-until-settled simplify`

Imagine an inner skill called `simplify` that proposes simplifications, but where two valid styles exist and each one looks like a "simplification" relative to the other — early-return-flat vs ternary-compact, say.

**Iterations 1–3.**
- Iter 1: refactors `formatPath` into early-return style. State `A`.
- Iter 2: re-analyzes, recommends ternary-compact style. State `B`.
- Iter 3: re-analyzes, recommends early-return again. State `A` (matches iteration 1's fingerprint).

**Cycle detected.** `FINGERPRINTS[3] == FINGERPRINTS[1]`.

**Resolution attempt:** the orchestrator reads the inner skill's reasoning at iteration 1 (state A) and at iteration 2 (state B):

- At A → B: "ternary is more compact (3 lines vs 7)."
- At B → A: "early returns are easier to extend; the ternary becomes unreadable if a fourth case is added; the function is documented in the API and likely to grow."

The orchestrator judges the iteration-2-to-A reasoning as substantively stronger (extensibility argument outweighs line-count argument), and picks **state A** without consulting the user. It restores state A via `git reset --hard <A-sha>`.

**Convergence summary:**

```
## Convergence summary

- Iterations: 3
- Exit reason: cycle resolved at iteration 3 ↔ iteration 1, kept state A (early-return-flat)
- Net change since start: 1 file changed, +4/-2 lines
- Notable events: 1 cycle (autonomously resolved — favored extensibility argument over compactness)

## Iteration log

| # | Outcome             | Net change                              |
|---|---------------------|-----------------------------------------|
| 1 | continuing          | refactored formatPath to early-return   |
| 2 | continuing          | rewrote formatPath as ternary           |
| 3 | cycled (resolved A) | reverted to state A                     |
```

The orchestrator does **not** auto-invoke a follow-up after cycle resolution — it would ask the user whether to proceed (e.g., "kept state A; want me to run `release`?"), since the user might want to inspect the resolved state first.

---

## Example 3 — Stalled after three iterations, paused

**User request:** `/repeat-until-settled improve-code-structure`

The codebase has a flaky integration test that fails inconsistently when the inner skill tries to land a particular refactor.

**Iteration 1.** Inner skill recommends extracting a shared validator. User approves. Phase 2 makes the change. Verification fails — flaky test. Phase 2 reverts. Phase 3 skipped (no changes landed). Phase 4 summary mentions one approved-but-reverted recommendation. post == pre. **Stall #1.**

**Iteration 2.** Inner skill (fresh context) re-analyzes, recommends the same extraction. User approves. Same verification failure. Same revert. post == pre. **Stall #2.**

**Iteration 3.** Same again. post == pre. **Stall #3.**

`consecutive_stalls == 3` → pause.

The orchestrator emits:

```
Stalled after 3 consecutive iterations. The inner skill keeps recommending
extracting a shared validator from src/orders/validation.ts, but the changes
aren't landing.

Looking at the iteration log, the recurring blocker appears to be:
verification failure on tests/integration/orders.spec.ts — the test fails
on this change with "timeout exceeded waiting for fixture", but the test
passes on the original code.

This is likely an orchestration-layer issue (something about how the
recommendation is being applied or how the test interacts with the change),
not necessarily a problem with the inner skill itself. The recommendation
itself looks reasonable — the test may be flaky, or the extraction may have
introduced a subtle async-ordering change.

How would you like to proceed?
- retry: try the same recommendation again (perhaps the flake clears)
- skip: drop this recommendation and continue iterating on others
- abandon: stop the loop and produce a partial convergence summary
- change scope: narrow or broaden what the inner skill is operating on
```

The user picks "skip". The orchestrator notes the skip, resets `consecutive_stalls = 0`, and continues to iteration 4 with a hint to the inner skill that the validator extraction has been deferred.
