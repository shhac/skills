---
name: repeat-until-settled
description: Repeatedly invokes a target skill until its output settles — meaning the target makes no further substantive changes or recommendations. Detects cycles (oscillation between two or more states) and stalls (inner skill keeps recommending but changes don't land) and handles each appropriately. Optionally chains to a follow-up skill after settling. Use when one pass of a skill is rarely enough and each pass tends to uncover more work until eventually there's none — e.g. "repeat-until-settled improve-code-structure then release".
---

# Repeat Until Settled

A meta-skill that runs another skill in a loop until the working state settles, then optionally chains to a follow-up. Use when one pass of a skill is rarely enough — when each pass uncovers more work until eventually nothing's left.

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

For three worked examples (settle in 3 iterations, cycle resolved autonomously, stall after 3 attempts), see [references/examples.md](references/examples.md).

### Setup

Before the first iteration:

1. **Pick a state-capture recipe.** Identify the project type and pick the appropriate recipe from [references/state-capture.md](references/state-capture.md): git project, plain filesystem, or ambiguous (ask the user). The recipe defines what counts as the "state" of the work and how to compare two states for equality. This skill is domain-agnostic — the inner skill might be operating on code, prose, artwork, configuration, anything — so don't assume a default; pick the recipe that fits.
2. **Capture `START_STATE`** using the chosen recipe.
3. Initialize empty list `STATES = []` (cycle detection will compare against this).
4. Initialize counters: `iteration = 0`, `consecutive_stalls = 0`, `forward_escape_attempts = 0`.
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

| Condition                                                                                          | Outcome      | Action                                                                                                       |
|----------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------|
| `post == pre` AND inner skill's summary indicates no further work                                  | **Settled**  | Exit loop → convergence summary → follow-up.                                                                 |
| `post == pre` AND inner skill's summary had recommendations or pending work                        | **Stalled**  | Increment `consecutive_stalls`. If `>= 3`, pause and ask. Otherwise reset for next iteration.                |
| `post` matches `STATES[i]` for some `i < iteration - 1` (not the immediately prior) AND the summaries are similar | **Cycled**   | Run cycle resolution. Reset `consecutive_stalls = 0`.                                                        |
| `post != pre` and not a cycle                                                                      | **Continuing** | Reset `consecutive_stalls = 0` and proceed to next iteration.                                              |

#### Settle detection — two signals must agree

- **State delta zero:** `post == pre` per the recipe.
- **Positive output signal:** the inner skill's summary contains an explicit empty/done indicator. Treat any of the following as positive:
  - An explicit "no findings" / "no recommendations" / "nothing to change" / "done" / "settled" statement.
  - A structured summary whose findings/recommendations list is empty.
  - A phase report whose accumulators are all empty / "none".

  If the summary is ambiguous (recommendations exist but were deferred, status is unstated, the inner skill returned terse text like "done." with no breakdown), default to **Stalled**, not Settled. Premature settle exits the loop and may invoke a follow-up against incomplete work.

State delta zero AND positive output signal → Settled. State delta zero AND ambiguous output → Stalled.

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

A **stall** is an iteration where the inner skill produced recommendations or had pending work, but no changes landed. Stalls usually indicate trouble at the *orchestration* layer, not inside the inner skill — verification keeps failing, user keeps rejecting, a tool keeps erroring, the same recommendation gets re-proposed but never applied.

After **three consecutive stalls**, pause the loop.

The pause message must clearly tell the user what the actual failure mode looks like, framed at the orchestration layer rather than blaming the inner skill:

```
Stalled after 3 consecutive iterations. The inner skill keeps recommending
{summary of recurring recommendation}, but the changes aren't landing.

Looking at the iteration log, the recurring blocker appears to be:
{verification failure on file X | user rejection | tool error: …}

This is likely an orchestration-layer issue (something about how the
recommendation is being applied), not necessarily a problem with the inner
skill itself.

How would you like to proceed?
- retry: try the same recommendation again
- skip: drop this recommendation and continue iterating
- abandon: stop the loop and produce a partial convergence summary
- change scope: narrow or broaden what the inner skill is operating on
```

Reset `consecutive_stalls` after the user responds.

### Convergence summary

Once the loop exits via Settled or Cycled-resolved (not by max-cap or abandon), output:

```
## Convergence summary

- Iterations: {N}
- Exit reason: {settled | settled-via-cycle (stay) | cycle resolved by forward-escape at iteration M ↔ K | partial: max-cap | partial: abandoned at stall}
- Net change since start: {recipe-appropriate metric — git diff stats, file count delta, word count delta, etc.}
- Notable events: {stalls encountered, cycles encountered, user decisions during the run; "none" if empty}

## Iteration log

| # | Outcome    | Net change                            |
|---|------------|---------------------------------------|
| 1 | continuing | refactored 3 files                    |
| 2 | continuing | extracted 2 shared utilities          |
| 3 | stalled→retried | (no change — verification failed) |
| 4 | continuing | applied alternate refactor            |
| 5 | settled    | (no change — nothing left to do)      |
```

If the loop exits via max-cap or user-abandon, label the summary "Partial convergence" instead and explain why.

### Follow-up

If a follow-up was parsed from the args and the loop reached **Settled** (not Cycled-resolved, not max-cap, not abandoned), invoke the follow-up as if the user had just typed it directly. Pass any args from the parsed follow-up invocation.

If the loop exited via Cycled-resolved, ask the user whether to proceed with the follow-up — they may want to verify the cycle-resolved state first before, e.g., releasing.

If the loop exited via max-cap or abandon, do **not** invoke the follow-up. Surface that to the user.

## Cross-harness notes

- **Skill invocation:** in Claude Code use the Skill tool; in the Claude Agent SDK use the equivalent subagent/skill API; in other harnesses use whatever mechanism that harness provides.
- **User pauses** (cycle requiring user input, stall threshold reached, no args given, max-cap exit): the pause mechanism depends on the harness — interactive prompt, return to caller, etc. What matters is that the loop does not advance without explicit input.
- **No backwards operations.** The skill never rolls back state — no `git reset`, no `git checkout` to a prior SHA, no overwriting newer files with older versions. Cycle resolution moves forward only (stay or forward-escape).
- **Domain-agnostic.** The inner skill might be operating on code in a git repo, prose in a manuscript directory, image files, configuration, anything. Use the appropriate state-capture recipe from references/state-capture.md; do not assume code or git unless the project shape says so.

## Limits

- **No iteration cap by default.** Without a user-specified cap, the loop runs to one of: settled, cycle-resolved, abandoned at the stall pause.
- **One follow-up.** v1 honors `<inner> then <follow-up>` only. Multi-step chains are not supported.
- **No resumability across sessions.** If the harness session ends mid-loop, the loop does not resume; the user re-invokes manually.
