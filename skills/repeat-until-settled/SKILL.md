---
name: repeat-until-settled
description: Repeatedly invokes a target skill until its output settles — meaning the target makes no further substantive changes or recommendations. Detects cycles (oscillation between two or more states) and stalls (inner skill keeps recommending but changes don't land) and handles each appropriately. Optionally chains to a follow-up skill after settling. Use when one pass of a skill is rarely enough and each pass tends to uncover more work until eventually there's none — e.g. "repeat-until-settled improve-code-structure then release".
---

# Repeat Until Settled

A meta-skill that runs another skill in a loop until the working state settles, then optionally chains to a follow-up. Use when one pass of a skill is rarely enough — when each pass uncovers more work until eventually nothing's left.

## Arguments

The skill takes one argument string of the form:

```
<inner-skill-invocation> [then <follow-up-invocation>]
```

Examples:

- `improve-code-structure`
- `improve-code-structure then release`
- `improve-code-structure src/auth.ts then release`
- `simplify the lib/ directory then commit`

Parse: split on the first ` then ` (case-insensitive, surrounded by whitespace).

- Left side = inner skill invocation (with its args).
- Right side, if present = follow-up invocation (with its args).

If no argument is supplied, ask the user what skill to repeat. If multiple ` then ` separators are present, only the first is honored in v1; extras are reported back to the user as ignored.

If the user expressed an iteration cap in natural language anywhere in the args ("up to 10 times", "max 5 iterations", "at most 20"), parse it out and respect it. Without an explicit cap, there is **no maximum** — the loop runs until settled, cycled, or stalled-out.

## Instructions

You are the **orchestrator** running an outer loop over a target skill.

Copy this checklist into your first response and tick items off as you progress:

```
- [ ] Parse arguments (target skill, optional follow-up, optional max)
- [ ] Capture starting state (HEAD SHA + working-tree hash)
- [ ] Iteration loop: invoke target → fingerprint → classify
- [ ] On settled or cycle-resolved: produce convergence summary
- [ ] On settled: invoke follow-up if specified
```

For three worked examples (settle in 3 iterations, cycle resolved autonomously, stall after 3 attempts), see [references/examples.md](references/examples.md).

### Setup

Before the first iteration:

1. Record `START_SHA = git rev-parse HEAD` and `START_TREE_HASH = sha256(git diff HEAD)`. Together these are the baseline.
2. Initialize an empty list `FINGERPRINTS = []` for cycle detection (each entry is a `(SHA, tree-hash)` tuple).
3. Initialize counters: `iteration = 0`, `consecutive_stalls = 0`.

### Per-iteration loop

For each iteration:

1. Increment `iteration`. If a max was specified and `iteration > max`, exit the loop and report the cap was hit (this is *not* settled — surface it explicitly).
2. **Capture pre-state:** `pre = (git rev-parse HEAD, sha256(git diff HEAD))`.
3. **Invoke the target skill** as if the user had just invoked it directly, with its parsed args. The mechanism depends on the harness — the Skill tool in Claude Code, the equivalent subagent/skill API in the Claude Agent SDK, equivalent constructs elsewhere.
4. **Capture post-state:** `post = (git rev-parse HEAD, sha256(git diff HEAD))`. Append `post` to `FINGERPRINTS`.
5. **Capture the inner skill's final summary** — the text it produced when it concluded. You'll need this for the settle/stall distinction below.
6. **Classify the outcome** using the table in the next section.

### Outcome classification

| Condition                                                                                          | Outcome      | Action                                                                                                       |
|----------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------|
| `post == pre` AND inner skill's summary indicates no further work                                  | **Settled**  | Exit loop → convergence summary → follow-up.                                                                 |
| `post == pre` AND inner skill's summary had recommendations or pending work                        | **Stalled**  | Increment `consecutive_stalls`. If `>= 3`, pause and ask. Otherwise reset for next iteration.                |
| `post` matches `FINGERPRINTS[i]` for some `i < iteration - 1` (not the immediately prior)          | **Cycled**   | Run cycle resolution. Reset `consecutive_stalls = 0`.                                                        |
| `post != pre` and not a cycle                                                                      | **Continuing** | Reset `consecutive_stalls = 0` and proceed to next iteration.                                              |

#### Settle detection — two signals must agree

- **Git delta zero:** `post == pre`. No commits, no working-tree change.
- **Output judgment:** the inner skill's final summary indicates no further work. Look for phrases like "no recommendations", "nothing to change", "no findings", an empty prioritized plan, an explicit "done" / "settled" message, or a Phase-N report whose accumulators are all "none". Read the actual summary; don't pattern-match blindly.

If git delta is zero but the inner skill *wanted* changes that didn't land, that's a **stall**, not a settle. They're distinct: settle = the world is stable; stall = the skill wanted to change things and couldn't.

### Cycle resolution

When the current fingerprint matches an earlier one (two or more iterations back), the loop has cycled. **Do not immediately return to the user** — try to resolve autonomously first.

1. Identify the cycle: which iterations are involved (e.g. iteration 5's state == iteration 2's state).
2. For each state in the cycle, gather the inner skill's reasoning at that point — what recommendations it produced, what justifications, what verification outcomes.
3. **Pick autonomously when possible.** Read the competing reasonings and choose the state with the stronger case — usually the one that addresses more concerns, or the one whose competing alternative carries weaker confidence in the inner skill's own words.
4. **Surface only when uncertain.** If the two sides are comparably strong and you cannot confidently pick, present both states to the user with a one-line summary of each side's reasoning, and ask which to keep. The pause mechanism depends on the harness.
5. Once a side is chosen, restore that state (`git checkout`/`git reset` to the corresponding commit, or apply/discard working-tree changes accordingly), exit the loop, record the choice in the convergence summary, and proceed to the follow-up if specified.

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
- Exit reason: {settled | cycle resolved at iteration M ↔ K}
- Net change since start: {diff stats — files changed, +additions, -deletions}
- Notable events: {stalls encountered, cycles encountered, user decisions during the run}

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
- **Git operations** are plain `git` — no Graphite, no `gh`, no harness-specific tooling.
- **Reversal of state** during cycle resolution may require committed history. If the inner skill commits between iterations, `git reset --hard <SHA>` works; if it leaves changes uncommitted, `git checkout -- .` plus restoring stashes is the pattern. If the inner skill's commit policy is unclear, ask the user before performing destructive resets.

## Limits

- **No iteration cap by default.** Without a user-specified cap, the loop runs to one of: settled, cycle-resolved, abandoned at the stall pause.
- **One follow-up.** v1 honors `<inner> then <follow-up>` only. Multi-step chains are not supported.
- **No resumability across sessions.** If the harness session ends mid-loop, the loop does not resume; the user re-invokes manually.
