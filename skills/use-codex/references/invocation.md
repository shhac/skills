# Codex CLI invocation reference

The commands below were checked against Codex CLI 0.169.0. For another version, start with `codex --version`, `codex exec --help`, or the relevant subcommand's help. See the [OpenAI non-interactive mode guide](https://learn.chatgpt.com/docs/non-interactive-mode) and [CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

## Model and reasoning

Use `-m gpt-6.1-sol -c 'model_reasoning_effort="high"'` for the skill's default. Set both explicitly because the CLI's defaults can differ. For routine work with clear acceptance criteria, consider lowering Sol's effort. If a task warrants a different model or effort, check the catalog for your configured provider with `codex debug models`. Add `--bundled` to inspect the catalog shipped with the binary without refreshing it.

## Input and permissions

- Pass the prompt as one quoted argument. Use `</dev/null` for a prompt-only run. Use `codex exec … - < "$prompt_file"` to read the prompt from a file. Piped stdin alongside a prompt argument becomes additional context.
- Choose the working root with `-C <dir>`. For authorized edits use `--sandbox workspace-write`. Add `--add-dir <dir>` if the task includes edits to another directory, or use `--worktree` for an isolated implementation in a managed Git worktree.
- Replace legacy `--full-auto` with `--sandbox workspace-write`. When the workflow calls for automatic approval review, `--approve-for-me` selects that approval mode along with workspace-write.
- To enable live search in an exec run, pass `-c 'web_search="live"'`. For screenshots or other images, pass `--image <file>` and put the prompt after the other flags, separated by `--` if it follows the image paths.

## Output and session IDs

By default, the final message goes to stdout and progress goes to stderr. `-o <file>` also saves the final message to a file. Check the process exit status before using either result, and use fresh paths for each run. Add `--output-schema <file>` when a downstream tool needs a final message that conforms to a JSON Schema.

Add `--json` to capture stdout as a stream of JSON Lines. With the same `repo_dir` and `prompt` as in the quick start:

```bash
run_dir=$(mktemp -d) &&
  codex exec -m gpt-6.1-sol -c 'model_reasoning_effort="high"' \
    --sandbox read-only -C "$repo_dir" --json \
    -o "$run_dir/final.txt" "$prompt" \
    </dev/null >"$run_dir/events.jsonl" 2>"$run_dir/progress.log" &&
  jq -er 'first(inputs | select(.type == "thread.started") | .thread_id)' \
    -n "$run_dir/events.jsonl"
```

Keep that UUID for follow-ups. For troubleshooting or tracking usage, look for `turn.failed`, `error`, and the `usage` object on `turn.completed`. Use `--ephemeral` for a one-shot run when you can discard the session history.

## Continue a session

Run from the intended project directory. Set `thread_id` to the ID from `thread.started` and `follow_up` to the new prompt.

```bash
codex exec resume -m gpt-6.1-sol -c 'model_reasoning_effort="high"' \
  -c 'sandbox_mode="read-only"' "$thread_id" "$follow_up" </dev/null
```

- Use an explicit ID when multiple runs may exist. `codex exec resume --last` selects the most recent recorded session for the current directory. Adding `--all` widens that search.
- Put follow-up options such as `-m`, `-c`, `--json`, and `-o` after `resume`. Use the `sandbox_mode` config override when using sandbox modes and setting permissions explicitly. Check `codex exec resume --help` for the available flags.
- Use `codex exec fork <session-id> <prompt>` to try a different approach in a new session with the same history. Omit the prompt to create the fork without starting a turn.

## Troubleshoot a failed run

Inspect stderr and, if using JSONL, the failure events. A message about reading additional stdin can appear with `</dev/null`; check whether the process is actually waiting for input. If the run fails the Git repository check, confirm the working directory and add `--skip-git-repo-check` for an intentional non-repo run. Check saved authentication with `codex login status` and broader installation, configuration, or runtime issues with `codex doctor`.
