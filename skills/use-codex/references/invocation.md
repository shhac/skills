# Codex CLI invocation reference

Verified against codex-cli 0.138.0 (local). Re-verify flags with `codex exec --help` if behaviour seems off — the CLI moves fast.

## Canonical one-shot invocation

```bash
codex exec \
  -m gpt-5.5 \
  -c model_reasoning_effort="medium" \
  --sandbox read-only \
  -C /path/to/repo \
  -o /tmp/codex-out.txt \
  "<prompt>" </dev/null 2>/dev/null
```

Then read `/tmp/codex-out.txt` — that file contains ONLY the final agent message.

Why each part matters:

| Part | Why |
|---|---|
| `-o <file>` / `--output-last-message <file>` | Writes only the final message. Read this file instead of stdout so intermediate agent activity never enters context. |
| `</dev/null` | `codex exec` always reads stdin and appends it to the prompt. Without this, a wrapper invocation can hang forever or slurp unintended input. |
| `2>/dev/null` | All intermediate activity (shell calls, reasoning summaries) streams to stderr; stdout carries only the final message. Discard stderr except when debugging a failing invocation. |
| `--sandbox <mode>` | `read-only` (default choice for questions/reviews), `workspace-write` (delegated implementation), `danger-full-access` (never, outside disposable environments). |
| `-C <dir>` | Working root for the agent. Prefer this over `cd`. |
| `-c model_reasoning_effort="..."` | `low` / `medium` / `high` / `xhigh`. Config-file default may be `high` — set explicitly per task. |

Additional useful flags:

- `--skip-git-repo-check` — required when running outside a git repo.
- `--ephemeral` — don't persist the session to disk. Use for throwaway one-shots; **incompatible with later resume**.
- `--output-schema <file>` — JSON Schema the final message must conform to. Use when the output feeds a script.
- `-i <image>` — attach image(s) to the prompt.
- `--add-dir <dir>` — extra writable directories alongside the workspace.
- `--search` — enable live web search for the agent.
- `-a never` / `--ask-for-approval never` — no approval prompts (exec is already non-interactive; only needed if a config profile sets a stricter policy).
- `--full-auto` is **deprecated** — use `--sandbox workspace-write` instead.

## Models and reasoning effort

There is **no `gpt-5.5-codex`** — the dedicated `-codex` model line ended at 5.3 (now deprecated); the frontier model `gpt-5.5` powers Codex directly.

| Model | Use for |
|---|---|
| `gpt-5.5` | Default. Best quality; ~40% fewer output tokens than gpt-5.4 for the same task. |
| `gpt-5.4-mini` | Quick, responsive subtasks; ~4x more quota headroom on ChatGPT plans. |
| `gpt-5.3-codex-spark` | Near-instant iteration (ChatGPT Pro-only research preview). |

Reasoning effort: `minimal | low | medium | high | xhigh` via `-c model_reasoning_effort="..."`. CLI default is `medium`, but `~/.codex/config.toml` may override it — set it explicitly per task rather than relying on the default. Use `low`/`medium` for lookups and mechanical work, `high`+ for gnarly implementation.

## Capturing the session ID

Use `--json` (JSONL events on stdout). The first event carries the ID:

```bash
codex exec --json -o /tmp/out.txt "<prompt>" </dev/null 2>/dev/null > /tmp/events.jsonl
head -1 /tmp/events.jsonl
# {"type":"thread.started","thread_id":"019f2e2f-0f79-7e10-b1b6-888370f69e87"}
```

Extract it without reading the whole stream:

```bash
THREAD_ID=$(head -1 /tmp/events.jsonl | sed 's/.*"thread_id":"\([^"]*\)".*/\1/')
```

The final `turn.completed` event includes token usage (`input_tokens`, `cached_input_tokens`, `output_tokens`) — useful for reporting spend. Don't read the events in between; that defeats the purpose.

Sessions also persist as `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl`; the trailing UUID is the session ID if the `--json` capture was lost.

## Resuming a session

```bash
codex exec resume <THREAD_ID> \
  -o /tmp/codex-out2.txt \
  "<follow-up prompt>" </dev/null 2>/dev/null
```

- `codex exec resume --last` resumes the most recent session (cwd-filtered; `--all` disables the filter) — prefer the explicit ID when multiple Codex runs may have happened.
- **`resume` does NOT accept `-s`/`--sandbox`** — the sandbox mode carries over from the original session. To change it, use `-c sandbox_mode="workspace-write"`.
- `resume` DOES accept `-m`, `-o`, `--json`, `--output-schema`, `-i`.
- Resumed turns replay the whole conversation as input tokens on Codex's side (cached, but not free) — resume when continuity matters, start fresh when it doesn't.

## Timeouts

Codex emits nothing to stdout until done (without `--json`), so give the Bash call a generous timeout scaled to reasoning effort:

| Effort | Timeout |
|---|---|
| low | 150s |
| medium | 300s |
| high | 600s |
| xhigh | 1200s |

For long jobs, prefer `run_in_background: true` on the Bash call and read the `-o` file when it completes, rather than blocking.

## Applying Codex's work

- With `--sandbox workspace-write`, Codex edits the working tree directly — review the resulting diff afterwards.
- With `read-only`, ask Codex to output a unified diff and apply it yourself, or re-run the task with write access once the approach is agreed.
- `codex apply` applies the latest diff produced by a Codex agent as a `git apply` — relevant for Codex Cloud tasks.

## Failure modes

- Exit code is non-zero on errors; the `-o` file is not written if the run fails — check for the file's existence before reading. With `--json`, prefer detecting `turn.failed` / `error` events over exit-code taxonomy (codes beyond zero/non-zero are undocumented).
- "Reading additional input from stdin..." in output means `</dev/null` was forgotten.
- Unrecognized-flag errors on `resume` usually mean a flag (like `-s`) that only `exec` accepts.
- Auth problems: `codex doctor` diagnoses install/auth/config health.
