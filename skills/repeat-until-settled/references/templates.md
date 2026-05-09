# Output templates

Literal templates for the two terminal-branch outputs: the stall pause and the convergence summary. These live in references because the orchestrator only renders them at specific points in the loop, not every iteration.

## Stall pause — first threshold

Used when `consecutive_stalls` reaches 3 for the first (or any pre-deeper) time. Substitute the bracketed fields.

```
Stalled after 3 consecutive iterations. The inner skill keeps recommending
{recurring recommendation}, but the changes aren't landing.

Recurring blocker: {verification failure | user rejection | tool error: …}.

This is likely an orchestration-layer issue, not a problem with the inner
skill itself.

How would you like to proceed?
- retry — try the same recommendation again
- skip — drop this recommendation and continue
- abandon — stop the loop and produce a partial convergence summary
- change scope — narrow or broaden what the inner skill is operating on
```

## Stall pause — deeper threshold

Used when `total_stalls >= 6` OR the first-threshold pause has been hit twice in this run. Drops `retry`; adds an explicit recommendation.

```
Stalled deeply: {total_stalls} stalls so far across {N} iterations, and
retry has not been working.

Recurring blocker: {verification failure | user rejection | tool error: …}.

I'd suggest `change scope` or `abandon` — repeating the same approach is
unlikely to succeed.

How would you like to proceed?
- skip — drop this recommendation and continue
- change scope — narrow or broaden what the inner skill is operating on
- abandon — stop the loop and produce a partial convergence summary
```

## Convergence summary

Output this structure. Use the header from the [exit-reason dispatch](../SKILL.md#exit-reason-dispatch) table — `Convergence summary` for clean exits or `Partial convergence` for partial ones.

```
## {Convergence summary | Partial convergence}

- Iterations: {N}
- Exit reason: {one of the eight from the dispatch table}
- Net change since start: {recipe-appropriate metric — git diff stats, file count delta, word count delta, etc.; computed from START_STATE vs final state}
- Notable events: {stalls encountered, cycles encountered, user decisions during the run; "none" if empty}

## Iteration log

| # | Outcome     | Resolution      | Change-metric                    |
|---|-------------|-----------------|----------------------------------|
| 1 | continuing  | —               | {recipe-appropriate metric}      |
| 2 | stalled     | retried         | (no change)                      |
| 3 | continuing  | —               | …                                |
| 4 | cycled      | stay            | (no change — cycled at iter 2)   |
```

Column shape is canonical:

- `Outcome` is one of `settled`, `stalled`, `cycled`, `continuing` — the four bare classifications. No compound labels.
- `Resolution` is the secondary action, where applicable: `retried`, `skipped`, `stay`, `forward-escape`, or `—` for outcomes with no resolution step (`continuing`, plain `settled`).
- `Change-metric` comes from `ITERATION_LOG` captured during the loop — do not invent. For non-changing iterations, write `(no change …)` with a brief reason.

For Partial summaries, add a final section explaining why the loop exited partially:

```
## Why partial

{One paragraph: which exit reason fired, what was attempted, what the
user can do to resume or finish manually.}
```
