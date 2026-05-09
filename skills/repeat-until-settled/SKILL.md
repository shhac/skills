---
name: repeat-until-settled
description: Repeatedly invokes a target skill until its output settles — meaning the target makes no further substantive changes or recommendations. Detects cycles (oscillation between two or more states) and stalls (inner skill keeps recommending but changes don't land) and handles each appropriately. Optionally chains to a follow-up skill after settling. Use when one pass of a skill is rarely enough and each pass tends to uncover more work until eventually there's none — e.g. "repeat-until-settled improve-code-structure then release".
---

# Repeat Until Settled

Run a target skill in a loop, classify each iteration's outcome, and exit on settle, cycle resolution, max-cap, or user decision at a stall pause.

## Arguments

The skill takes one argument string of the form:

```
<inner-skill-invocation> [then <follow-up-invocation>] [max=N]
```

Examples:

- `improve-code-structure`
- `improve-code-structure then release`
- `improve-code-structure src/auth.ts then release`
- `simplify the lib/ directory then commit`
- `improve-code-structure max=10 then release`

### Parsing recipe

Apply these steps in order; each operates on the result of the previous one. This is the canonical recipe — do not improvise.

1. **Empty argument** → ask the user what skill to repeat. Stop.
2. **Extract iteration cap.** Look for an explicit `max=N` token (literal, with `=`, anywhere in the string). If present, set `max = N` and remove the token from the string. The literal `max=N` form is the only recognized cap syntax — natural-language phrases like "up to 10 times" are NOT parsed automatically, because they collide too easily with inner-skill args meaning the same words. If the user wrote a natural-language cap, surface a one-line note: "I see what looks like an iteration cap in your request. Please re-invoke with `max=N` to apply it, or confirm you want me to ignore it."
3. **Split on the follow-up separator.** Search for the first ` then ` (case-insensitive, with whitespace on both sides) in the remaining string.
4. **Validate the split.**
   - Left side = inner skill invocation. Must be non-empty.
   - Right side, if present = follow-up invocation. **Sanity-check:** if the right side does not begin with what looks like a skill name (single token of lowercase letters/numbers/hyphens), treat the split as a false positive — the inner skill's args legitimately contained " then ". In that case, treat the entire pre-cap string as the inner-skill invocation and report "no follow-up parsed".
5. **Multiple ` then ` separators** in the original string: only the first is honored. Report any extras as ignored.

Without an explicit `max=`, there is **no maximum** — the loop runs until settled, cycled, or stalled-out at the user-pause threshold.

## Instructions

You are the **orchestrator** running an outer loop over a target skill.

Copy this checklist into your first response and tick items off as you progress:

```
- [ ] Parse arguments (inner skill, optional follow-up, optional `max=N`)
- [ ] Pick state-capture recipe and capture `START_STATE`
- [ ] Iteration loop: capture pre → invoke inner skill → capture post → classify
- [ ] On Settled or Cycled-stay or Cycled-forward-resolved: produce convergence summary
- [ ] On Settled or Cycled-forward-resolved (with user OK): invoke follow-up if specified
```

For five worked examples covering settle, cycle-by-stay, cycle-by-forward-escape, a non-code (manuscript) project, and a stall pause, see [references/examples.md](references/examples.md).

### Setup

Before the first iteration:

1. **Pick a state-capture recipe.** Identify the project type and pick the appropriate recipe from [references/state-capture.md](references/state-capture.md): git project, plain filesystem, or ambiguous (ask the user). The recipe defines what counts as the "state" of the work and how to compare two states for equality. This skill is domain-agnostic — the inner skill might be operating on code, prose, artwork, configuration, anything — so don't assume a default; pick the recipe that fits.
2. **Capture `START_STATE`** using the chosen recipe.
3. Initialize empty list `STATES = []` (cycle detection will compare against this).
4. Initialize counters: `iteration = 0`, `consecutive_stalls = 0`, `total_stalls = 0`, `forward_escape_attempts = 0`, `first_pause_count = 0`.
5. Initialize empty list `ITERATION_LOG = []` (per-iteration data for the convergence summary).

### Per-iteration loop

For each iteration:

1. Increment `iteration`. If a max was specified and `iteration > max`, exit the loop with `Partial convergence (max-cap)`.
2. **Capture pre-state:** `pre = current state` (apply the chosen recipe from references/state-capture.md).
3. **Invoke the target skill** as if the user had just invoked it directly, with its parsed args. The mechanism depends on the harness — the Skill tool in Claude Code, the equivalent subagent/skill API in the Claude Agent SDK, equivalent constructs elsewhere.
4. **Capture post-state:** `post = current state` (same recipe). Append `post` to `STATES`.
5. **Capture the inner skill's final summary** — the text it produced when it concluded.
6. **Append per-iteration data to `ITERATION_LOG`:** the iteration number, outcome (after step 7), summary tag, and the recipe's change-metric (diff stats for git, file count for filesystem, word-count delta for text projects, etc.). Needed for the convergence summary.
7. **Classify the outcome** using the table in the next section.

### Outcome classification

| Outcome    | Condition                                                                                              | Action      |
|------------|--------------------------------------------------------------------------------------------------------|-------------|
| Settled    | `post == pre` AND summary has a positive empty/done signal (see [Settle predicate](#settle-predicate)) | → settle    |
| Stalled    | `post == pre` AND summary is ambiguous or had pending work                                             | → stall     |
| Cycled     | `post == STATES[i]` for some `i < iteration - 1` AND summary similar to that iteration's              | → cycle     |
| Continuing | otherwise                                                                                              | → continue  |

**Counter invariants** (apply on every iteration, regardless of outcome):

- `consecutive_stalls`: incremented in `→ stall`; reset to 0 in `→ continue`, `→ cycle`, and after the user responds to a stall pause. Untouched by `→ settle` (loop exits).
- `total_stalls`: incremented in `→ stall`; never reset. Used by [Stall handling](#stall-handling) to detect the deeper-stall threshold.
- `first_pause_count`: incremented in [Stall handling](#stall-handling) when the first-threshold pause is reached; never reset. Used together with `total_stalls` to detect the deeper-stall threshold.
- `forward_escape_attempts`: managed inside `→ cycle` only.
- `STATES`: `post` is appended on every iteration (already done in step 5 of the loop).

#### → settle

Exit the loop. Proceed to the [exit-reason dispatch](#exit-reason-dispatch).

#### → stall

Increment `consecutive_stalls`. If it reaches 3, run [Stall handling](#stall-handling) (pause and ask the user). Otherwise proceed to the next iteration without resetting the counter.

#### → cycle

Run [Cycle resolution](#cycle-resolution).

#### → continue

Proceed to the next iteration.

#### Settle predicate

Settle requires both signals:

- **State delta zero:** `post == pre` per the chosen recipe.
- **Positive output signal:** the inner skill's summary contains an explicit empty/done indicator. Treat any of these as positive:
  - "no findings" / "no recommendations" / "nothing to change" / "done" / "settled"
  - A structured summary whose findings / recommendations list is empty
  - A phase report whose accumulators are all empty / "none"

If state delta is zero but the summary is ambiguous (recommendations exist but were deferred, status is unstated, terse text like "done." with no breakdown), classify as Stalled, not Settled. Premature settle exits the loop and may invoke a follow-up against incomplete work.

### Cycle resolution

When `post` matches `STATES[i]` for some `i < iteration - 1` AND the inner skill's summary at iteration `i` is substantively similar to the current summary, the loop has cycled. (Summary similarity matters — two unrelated iterations can produce identical states by coincidence; without summary confirmation, the orchestrator would resolve a false cycle.)

**This skill never goes backward.** No `git reset`, no checkout to a prior SHA, no overwriting newer files with older versions. Cycles resolve forward, with one of two outcomes:

#### Stay

The current state is a fixed point — both sides of the cycle are valid and the inner skill is oscillating between equally-good options. This is the most common cycle pattern in LLM-driven loops.

- Default in: when the two competing summaries are comparably defensible (no asymmetric coverage advantage to either side).
- Action: exit the loop. Treat as `Settled-via-cycle`. The convergence summary records both sides' reasoning so the user sees what was at stake and why staying was reasonable.

#### Forward escape

The alternate state in the cycle has clearly stronger reasoning AND it isn't the current state — the inner skill is converging on the *worse* of the two options.

- Default in: when one side covers a concern the other doesn't (asymmetric coverage), AND the favored side is the alternate, not the current.
- Action: increment `forward_escape_attempts`. On the next iteration, prepend a directive to the inner skill: *"You have oscillated between state A and state B. State {favored} is preferred because {asymmetric-coverage reason}. Make the forward changes needed to land at {favored} and stay there."* Continue the loop. If `forward_escape_attempts >= 2` (the inner skill ignored the directive and produced another cycle), surface to the user — autonomous escape is not working.

#### Surface to user

When neither default applies — typically because the two sides are both substantive but disagree on a value judgment (style preference, scope tradeoff) the user should weigh in on.

- Action: present both states with their summaries and offer three options: **stay** at current, **forward-escape** to alternate, or **abandon** the loop. Pause for response. The pause mechanism depends on the harness.

### Stall handling

A **stall** is an iteration where the inner skill produced recommendations or had pending work, but no changes landed. Stalls usually indicate trouble at the *orchestration* layer, not the inner skill — verification keeps failing, user keeps rejecting, a tool keeps erroring, the same recommendation gets re-proposed but never applied.

Track two counters:

- `consecutive_stalls` — resets after the user responds to a pause.
- `total_stalls` — monotonic; never reset until the loop exits.

#### First-pause threshold

When `consecutive_stalls` reaches 3, increment `first_pause_count`. If `first_pause_count >= 2` OR `total_stalls >= 6`, jump to the [Deeper-stall threshold](#deeper-stall-threshold) below instead of the first-threshold pause — at this point retry has demonstrably not worked. Otherwise, pause using the [first-threshold template](references/templates.md#stall-pause--first-threshold) — offers **retry / skip / abandon / change scope**. After the user responds, reset `consecutive_stalls = 0`.

#### Deeper-stall threshold

Triggered when `first_pause_count >= 2` OR `total_stalls >= 6`. Pause using the [deeper-threshold template](references/templates.md#stall-pause--deeper-threshold) — drops `retry`, recommends `change scope` or `abandon`. After the user responds, reset `consecutive_stalls = 0` (but `first_pause_count` and `total_stalls` keep accumulating).

#### Ambiguous user response

If the user's response isn't a clear match to one of the offered options ("ok", "sure", "yeah whatever"), state your interpretation back before acting: "I read that as `retry` — please confirm or tell me a different option." Do not proceed on a guess. Treat ambiguous responses as a pause continuation, not a fresh decision.

### Exit-reason dispatch

When the loop exits, classify the exit reason and dispatch:

| Exit reason                                  | Summary header        | Follow-up                                |
|----------------------------------------------|-----------------------|------------------------------------------|
| Settled                                      | Convergence summary   | Invoke automatically.                    |
| Settled-via-cycle (Stay)                     | Convergence summary   | Ask user before invoking — they may want to verify the cycled state. |
| Forward-escape resolved (later settled)      | Convergence summary   | Invoke automatically — the resolution landed forward, the state is the natural outcome. |
| Partial: max-cap hit                         | Partial convergence   | Skip; surface to user.                   |
| Partial: abandoned at stall pause            | Partial convergence   | Skip; surface to user.                   |
| Partial: cycle surfaced, user picked abandon | Partial convergence   | Skip; surface to user.                   |
| Partial: forward-escape failed (≥2 attempts) | Partial convergence   | Skip; surface to user.                   |
| Partial: indeterminate (non-interactive harness, pause needed) | Partial convergence | Skip; state written to `.ai-cache/repeat-until-settled-state.md` for resume. |

The "Forward-escape resolved" row applies when forward-escape was invoked at some point but the loop later reached Settled — that's a clean exit, the cycle was a passing turbulence, not a terminal state.

### Convergence summary

Output the [convergence summary template](references/templates.md#convergence-summary), substituting the header from the dispatch table (`Convergence summary` for clean exits, `Partial convergence` for partial ones). Data for the iteration log comes from `ITERATION_LOG` captured during the per-iteration loop — do not invent it.

## Cross-harness notes

- **Skill invocation:** in Claude Code use the Skill tool; in the Claude Agent SDK use the equivalent subagent/skill API; in other harnesses use whatever mechanism that harness provides.
- **User pauses** (cycle requiring user input, stall threshold reached, no args given, ambiguous user response): the pause mechanism depends on the harness — interactive prompt, return to caller, etc. What matters is that the loop does not advance without explicit input.
- **Non-interactive harnesses.** Some harnesses can't pause for user input (scheduled runs, headless API invocations, CI). Detect this at Setup. When pauses aren't supported, the orchestrator must NOT autonomously decide things that would normally pause — never invent a stall response, never auto-pick on a "Surface to user" cycle. Instead, exit with `Partial: indeterminate`, write the loop state and the pending question to a discoverable location (e.g. `.ai-cache/repeat-until-settled-state.md`), and stop. The user can re-invoke later with the answer.
- **No backwards operations.** The skill never rolls back state — no `git reset`, no `git checkout` to a prior SHA, no overwriting newer files with older versions. Cycle resolution moves forward only (stay or forward-escape).
- **Domain-agnostic.** The inner skill might be operating on code in a git repo, prose in a manuscript directory, image files, configuration, anything. Use the appropriate state-capture recipe from references/state-capture.md; do not assume code or git unless the project shape says so.

## Limits

- **No iteration cap by default.** Without a user-specified cap, the loop runs to one of: settled, cycle-resolved, abandoned at the stall pause.
- **One follow-up.** v1 honors `<inner> then <follow-up>` only. Multi-step chains are not supported.
- **No resumability across sessions.** If the harness session ends mid-loop, the loop does not resume; the user re-invokes manually.
