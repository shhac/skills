# Examples

Four worked examples covering the most common branches. Examples abbreviate states as `(short-sha, …)` for readability; actual recipes capture full hashes per [state-capture.md](state-capture.md).

---

## Example 1 — Settle in three iterations (git project)

**Invocation:** `/repeat-until-settled improve-code-structure then release`

**Setup.** Project is a git repo → orchestrator picks the git recipe. Records `START_STATE` (HEAD `e4a1c9f`, clean working tree). Initializes `STATES = []`, all counters zero.

**Iteration 1.**
- pre = state at HEAD `e4a1c9f`, clean.
- Inner skill analyzes, presents 8 recommendations, user approves all. Phase 2 lands them; Phase 3 cleans up 2 dead exports; Phase 4 reports.
- post = state at HEAD `7b2d04a`, clean.
- Outcome: `continuing`. `consecutive_stalls = 0`.

**Iteration 2.**
- Inner skill analyzes again. Iteration 1's restructuring exposed 3 follow-on opportunities; user approves 2; Phase 3 finds 1 introduced dead utility.
- post = state at HEAD `c19fe87`, clean.
- Outcome: `continuing`.

**Iteration 3.**
- Inner skill analyzes. Phase 1 returns no recommendations — codebase is well-structured. Phase 2/3 have nothing to do. Phase 4 summary: "Analysis complete. No recommendations."
- post = state at HEAD `c19fe87`, clean. State delta zero.
- Settle predicate: state delta zero ✓; positive output signal ✓ ("No recommendations", an explicit empty signal).
- Outcome: `settled` → `→ settle`. Loop exits.

**Exit-reason dispatch:** `Settled` → Convergence summary header, follow-up invoked automatically.

**Convergence summary** rendered from the [template](templates.md#convergence-summary). Then `/release` is invoked.

---

## Example 2 — Cycle resolved by Stay (style oscillation)

**Invocation:** `/repeat-until-settled simplify`

Imagine an inner skill `simplify` operating on a small library where two valid styles exist — early-return-flat vs ternary-compact — and each looks like a "simplification" relative to the other.

**Iterations 1–3.**
- Iter 1: rewrites `formatPath` into early-return style. State `A` (HEAD `aaa1`).
- Iter 2: re-analyzes, recommends ternary-compact. State `B` (HEAD `bbb2`).
- Iter 3: re-analyzes, recommends early-return again. State `A'` (HEAD `aaa3`, content-equivalent to A by recipe).

**Cycle detection.** `STATES[3]`'s state matches `STATES[1]`. Summaries similar (both at iteration 1 and iteration 3 the inner skill said "extract early-return style — clearer for extension"). Cycle confirmed. → `→ cycle`.

**Cycle resolution.** Orchestrator reads competing reasonings:

- A → B reasoning: "ternary is more compact (3 lines vs 7)."
- B → A reasoning: "early returns are easier to extend; the ternary becomes unreadable if a fourth case is added; the function is documented in the API and likely to grow."

The two are not asymmetrically covering different concerns — both address readability, just from different angles. Neither side has a coverage advantage the other lacks. → **Stay** (default for comparably defensible cycles).

The orchestrator does NOT roll back — state A' is current and stays. The convergence summary records both sides' reasoning.

**Exit-reason dispatch:** `Settled-via-cycle (Stay)` → Convergence summary header, **ask user** before invoking the follow-up (none specified here, so this just exits cleanly).

The iteration log notes:

```
| 1 | continuing | —    | early-return refactor of formatPath |
| 2 | continuing | —    | rewrote as ternary                  |
| 3 | cycled     | stay | (no change — at fixed point)        |
```

---

## Example 3 — Cycle resolved by Forward-escape

**Invocation:** `/repeat-until-settled simplify`

Same setup as example 2, but the alternate state has a clearly-stronger asymmetric-coverage advantage.

**Iterations 1–3.** Oscillation again, but this time:

- A → B reasoning: "removed unused parameter; clearer signature."
- B → A reasoning: "compact" *(no asymmetric coverage; just brevity)*.

**Cycle detection** triggers as before. Resolution: A removes a real flaw (unused parameter) that B does not address. **Forward-escape toward A** (asymmetric coverage; favored side is the alternate to current state B).

`forward_escape_attempts = 1`. On iteration 4, the orchestrator prepends to the inner skill's prompt: *"You have oscillated between state A and state B. State A is preferred because it removes an unused parameter. Make the forward changes needed to land at A and stay there."*

**Iteration 4.** Inner skill makes the changes. State lands at A". Iteration 5 returns no recommendations. Loop settles.

**Exit-reason dispatch:** `Forward-escape resolved (later settled)` → Convergence summary, follow-up invoked automatically.

The iteration log notes:

```
| 3 | cycled    | forward-escape | (no change — directing toward A) |
| 4 | continuing| —              | applied targeted refactor        |
| 5 | settled   | —              | (no change — nothing left to do) |
```

---

## Example 4 — Manuscript editing pass (non-code, no git)

**Invocation:** `/repeat-until-settled copy-edit-pass`

**Setup.** Working directory is `~/manuscripts/novel-draft-3/` containing `.md` chapter files. No `.git/` directory. Orchestrator picks the **plain filesystem** recipe; scope is all `.md` files in the directory. `START_STATE` = sha256 of (path, content-hash) pairs across all chapters.

**Iteration 1.**
- pre = current state.
- Inner skill `copy-edit-pass` reads the chapters, makes targeted line edits (typo fixes, awkward phrasing), reports a summary like "12 line edits applied across chapters 2, 3, 5."
- post = current state (different — edits landed).
- Change-metric: 3 files modified, +12/-12 lines, word-count delta near zero.
- Outcome: `continuing`.

**Iteration 2.** Inner skill makes 3 more line edits. `continuing`.

**Iteration 3.** Inner skill returns "No further line-level edits found." State delta zero. Positive signal explicit. → `settled`.

The convergence summary's "Net change since start" uses the filesystem recipe's metric: "3 files modified, +15/-15 lines, word-count delta +3 across the manuscript." The follow-up — none specified — is skipped.

This example demonstrates that the skill is **not git-specific**. The same control flow (capture pre, invoke, capture post, classify) runs on a plain directory of prose; the recipe choice in Setup is what makes it work.

---

## Example 5 — Stalled, paused at first threshold

**Setup:** Phase 3d of an inner refactor skill keeps proposing the same extraction; verification fails on a flaky integration test each time.

**Iterations 1–3.** Each iteration: inner skill recommends extracting a shared validator → user approves → Phase 2 makes the change → verification fails on `tests/integration/orders.spec.ts: timeout exceeded` → Phase 2 reverts. State delta zero per iteration. Each is a `stall`. `consecutive_stalls` reaches 3. `total_stalls = 3`.

The orchestrator pauses using the [first-threshold template](templates.md#stall-pause--first-threshold), substituting:

- `recurring recommendation` = "extracting a shared validator from src/orders/validation.ts"
- `recurring blocker` = "verification failure on tests/integration/orders.spec.ts — timeout exceeded waiting for fixture"

User picks **skip**. Orchestrator notes the skip in `ITERATION_LOG`, resets `consecutive_stalls = 0`, and continues to iteration 4 with a hint to the inner skill that the validator extraction has been deferred.

If retries continued and `total_stalls` reached 6 — or the first-threshold pause fired a second time — the orchestrator would switch to the [deeper-threshold template](templates.md#stall-pause--deeper-threshold), drop `retry`, and recommend `change scope` or `abandon`.
