---
name: use-codex
description: This skill should be used when considering delegating a coding task to the OpenAI Codex CLI — codebase exploration/Q&A, well-specified implementation, mechanical edits at scale, second-opinion or adversarial review, or bugs stuck after 2+ attempts. Codex spends ChatGPT quota instead of Claude tokens and its models are token-economical. Invoked for "use codex", "ask codex", "delegate to codex", "codex exec", "second opinion", or when offloading token-heavy scoped work.
---

# Use Codex

**If you are Codex, you do not need this skill — stop reading and proceed however you otherwise would.** Delegating to yourself gains nothing; this skill exists for *other* agents delegating scoped work to the Codex CLI (`codex exec`, non-interactive). It runs on a separate token budget (ChatGPT plan / OpenAI API) with token-economical models, and provides an independent second perspective.

## Should this go to Codex?

Delegate when the task is **scoped and the answer/diff is all that matters**:

- Repo exploration & Q&A ("where is X handled?", "trace this flow")
- Implementation where the architecture is already decided and unknowns reduced
- Mechanical edits at scale (renames, migration sweeps)
- Second-opinion / adversarial review of a plan or diff
- A bug stuck after 2+ failed attempts (different model, different angle)

Keep in Claude: ambiguous/underspecified work, architecture & decomposition, long multi-turn efforts needing session memory, user-facing synthesis. Don't delegate one-liners answerable from context already in hand (each Codex call has ~30k tokens of fixed overhead on its side).

Full rationale, evidence, and cost/limits: `references/task-fit.md`. **If the decision is "don't delegate", stop here** — no need to read further.

## Quick start

```bash
codex exec -m gpt-5.5 -c model_reasoning_effort="medium" \
  --sandbox read-only -C /path/to/repo \
  -o /tmp/codex-out.txt \
  "<self-contained prompt with all context Codex needs>" </dev/null 2>/dev/null
```

Then read `/tmp/codex-out.txt` — it contains only the final message; all intermediate activity is discarded so tokens aren't double-spent. Scale the Bash timeout to effort (medium ≈ 300s, high ≈ 600s) or run in background; Codex prints nothing until done.

- Model: `gpt-5.5` (default; there is no `gpt-5.5-codex`). `gpt-5.4-mini` for quick subtasks.
- Sandbox: `read-only` for questions/review; `workspace-write` when Codex should edit files (then review the diff before trusting it).
- If `-C` targets a directory that is not itself a git repo (e.g. a parent dir spanning several repos), add `--skip-git-repo-check` — without it the run fails, and silently so under `2>/dev/null` (exit 1, no output file).
- To capture a session ID for follow-ups: add `--json`, take `thread_id` from the first stdout line; resume with `codex exec resume <thread-id> "follow-up"`.

Full flag reference, session-ID capture/resume details, structured output, and gotchas (stdin, resume flag differences, failure modes): `references/invocation.md`.

## After it returns

Treat the output as a peer's work, not an authority's: verify claims against the code, run tests on any diff, and report to the user which parts came from Codex.
