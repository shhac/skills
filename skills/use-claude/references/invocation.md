# Claude Code headless invocation reference

Verified against Claude Code 2.1.201 (local). Re-verify flags with `claude --help` if behaviour seems off — the CLI moves fast.

## Canonical one-shot invocation

```bash
claude -p --output-format json --model sonnet \
  --tools="Read,Grep,Glob" \
  "<prompt>" > /tmp/claude-out.json
```

Then extract what's needed:

```bash
python3 -c 'import json;d=json.load(open("/tmp/claude-out.json"));print(d["result"])'
# or: jq -r .result /tmp/claude-out.json
```

Why each part matters:

| Part | Why |
|---|---|
| `-p` / `--print` | Headless mode: run to completion, print, exit. Nothing is emitted until done — intermediate agent activity never appears on stdout (unlike streaming modes), so it can't be double-read. |
| `--output-format json` | One JSON object: `.result` (final message), `.session_id` (for resume), `.total_cost_usd`, `.is_error`, `.usage`, `.permission_denials`. Default `text` prints only the final message; `stream-json` streams every event (use only when live progress is genuinely needed). |
| `--model <alias>` | `haiku` (fast/cheap) / `sonnet` (workhorse) / `opus` / `fable` (most capable; availability varies by plan). Full model IDs also accepted. |
| `--tools="..."` | Restrict the built-in toolset. `--tools="Read,Grep,Glob"` ≈ read-only analysis; `--tools=""` disables all tools (pure reasoning); omit for the full set. |

**Variadic-flag gotcha:** `--tools`, `--allowedTools`, `--add-dir` consume multiple following arguments. `--tools "" "prompt"` eats the prompt (error: "Input must be provided either through stdin or as a prompt argument"). Always use `=` syntax when a prompt follows: `--tools=""`.

Additional useful flags:

- `--effort low|medium|high|xhigh|max` — reasoning effort for the session.
- `--add-dir <dir>` — grant tool access to extra directories.
- `--append-system-prompt "<text>"` — add constraints without replacing defaults.
- `--fork-session` — on resume, branch into a new session ID instead of extending the original.
- `--session-id <uuid>` — pre-pick the session ID (must be a valid UUID).
- `-C <dir>` equivalent: none — run with the target repo as cwd so project CLAUDE.md, settings, and skills load.

## Permission ladder

Headless mode cannot prompt, so anything not pre-authorized is auto-denied (denials appear in `.permission_denials`, and the run continues without those tools).

1. **Read-only analysis** — `--tools="Read,Grep,Glob"`; nothing to authorize.
2. **Edits allowed** — `--permission-mode acceptEdits` (file edits auto-approved; Bash still gated).
3. **Granular** — `--allowedTools "Edit,Bash(git diff:*),Bash(npm test:*)"` — allowlist exact tools/command patterns.
4. **Everything** — `--dangerously-skip-permissions`; only inside an externally sandboxed environment.

With write access, review the resulting diff before trusting it.

## Capturing the session ID and resuming

`.session_id` is in the JSON result. Resume non-interactively:

```bash
claude -p --resume <SESSION_ID> --output-format json "<follow-up prompt>"
```

- Resume keeps the same session ID and full conversation context (verified: follow-ups see earlier turns).
- `claude -p -c "<follow-up>"` continues the most recent conversation in the current directory — prefer the explicit ID when multiple runs may have happened.
- `--fork-session` branches instead of extending — useful for trying two follow-up directions from one base run.
- Resumed turns replay conversation history as input tokens (cached, but not free) — resume when continuity matters, start fresh when it doesn't.

## Piping input

Stdin becomes part of the prompt: `git diff | claude -p "review this diff"`. With a prompt argument and no piped stdin, `claude -p` does not block waiting for input (no `</dev/null` needed, unlike some other CLIs).

## Timeouts

Nothing prints until the run completes, so allow generous wall-clock time scaled to task size and effort — minutes, not seconds, for multi-file work. For long jobs, run in the background and read the output file on completion rather than blocking.

## Failure modes

- Check `.is_error` and `.subtype` in the JSON result rather than relying on exit codes.
- Empty output + "Input must be provided..." error → a variadic flag swallowed the prompt (use `=` syntax).
- Unexpected refusals to act → check `.permission_denials`; the needed tool wasn't pre-authorized.
- `claude doctor` diagnoses install/auth health.

## Fixed overhead

A trivial tool-less call measured ~7k input tokens of system-prompt overhead; real calls in a configured repo (CLAUDE.md, MCP servers, skills) carry more. Don't delegate questions the caller can already answer from context in hand.
