---
name: use-claude
description: This skill should be used when a non-Claude agent (e.g. Codex) is considering delegating a coding task to Claude Code's headless mode (claude -p) — hard long-horizon bug fixing, implementation where first-pass completeness matters more than token cost, test authoring, or a cross-model-family second opinion on a plan or diff. Claude Code spends an Anthropic subscription/API budget instead of the caller's tokens. Invoked for "use claude", "ask claude", "delegate to claude", "claude -p", or "second opinion from claude".
---

# Use Claude

**If you are Claude, you do not need this skill — stop reading and proceed however you otherwise would.** Delegating to yourself gains nothing; this skill exists for *other* agents delegating scoped work to Claude Code's headless mode (`claude -p`).

## Should this go to Claude?

Delegate when the task is **scoped, hard, and correctness matters more than token cost**:

- Implementation where first-pass completeness counts — Claude spends more tokens but blind reviewers rate its output more complete
- Long-horizon debugging in real repos (multi-file root causes, tangled state)
- Test authoring and verification-heavy work
- Cross-family second opinion / adversarial review of a plan or diff (a different model family catches different bugs)
- Repo work that benefits from project context — Claude Code auto-loads the repo's CLAUDE.md, memory, and skills

A headless one-shot cannot interview the user, so ambiguous or underspecified work, open architecture decisions, and anything needing a long conversation are **not delegation targets** — they belong to whoever holds the user conversation. Reduce unknowns first, then delegate the well-specified remainder. Also skip delegation for cheap mechanical sweeps if the caller is the more token-efficient model — Claude's edge is quality, not thrift.

Full rationale, evidence, and cost notes: `references/task-fit.md`. **If the decision is "don't delegate", stop here** — no need to read further.

## Quick start

```bash
claude -p --output-format json --model sonnet \
  --tools="Read,Grep,Glob" \
  "<self-contained prompt with all context Claude needs>" > /tmp/claude-out.json
```

Headless mode emits nothing until done, then a single JSON object: `.result` is the final message (intermediate activity is never printed, so tokens aren't double-spent), `.session_id` enables follow-ups, `.total_cost_usd` reports spend.

- Models: `sonnet` (workhorse), `haiku` (quick lookups), `opus` / `fable` (hardest work); `--effort low|medium|high|xhigh|max`.
- Write access: default denies edits; add `--permission-mode acceptEdits` and/or `--allowedTools` when Claude should change files (then review the diff).
- Resume: `claude -p --resume <session-id> "follow-up"` keeps full context.
- Gotcha: variadic flags like `--tools` swallow a following prompt — use `=` syntax (`--tools="Read,Grep"`).

Full flag reference, permission ladder, session resume, piping, and failure modes: `references/invocation.md`.

## After it returns

Treat the output as a peer's work, not an authority's: verify claims against the code, run tests on any diff, and attribute Claude's contribution when reporting.
