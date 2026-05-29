# Dead code detection & cleanup

Refactoring removes callers, splits files, and shuffles exports — orphaned code and unreachable branches accumulate as a side effect. This phase finds and removes them, with safety checks at every step.

**Skip condition:** if Phase 2 made no changes (user approved nothing, or all changes were reverted), skip this phase entirely.

## Preconditions

The lead must have:

- Recorded the **baseline ref** at the start of Phase 2 — the git SHA the working tree was on before the first change. Step 3a's scan scope is computed by diffing against this exact ref.
- Completed all approved Phase 2 changes.

## Step 3a — Determine scan scope

Compute the scan scope from the baseline ref:

```
git diff --name-only <baseline-ref>...HEAD
```

That output is `CHANGED` — the files modified in Phase 2.

Then expand `CHANGED` to its **import neighbors**, in both directions and at both points in time:

| Axis    | Direction    | Why                                                      |
|---------|--------------|----------------------------------------------------------|
| current | imports from | Catches new orphans introduced by the refactor.          |
| current | imported by  | Catches files whose API surface may have shrunk.         |
| pre     | imports from | Catches files that lost their last caller during refactor. |
| pre     | imported by  | Catches files the refactor stopped importing.            |

Pre-refactor neighbors are recovered by inspecting `git diff <baseline-ref>...HEAD` for removed import lines in the changed files, then resolving the corresponding paths.

Union `CHANGED` with the four neighbor sets to form `SCOPE` — the input to Steps 3b and 3c.

Import syntax is language-specific (JS `import`, Python `import`/`from`, Go `import`, OCaml `open`, F# `open`, Erlang/Elixir `-import`/`alias`/`import`/`use`, etc.). The lead does not need to parse imports itself — assembling the candidate file set from `git diff` output is enough; the broad scanner subagent in 3b handles language-specific resolution within `SCOPE`.

## Step 3b — Broad scan (single subagent)

Spawn one subagent per the [subagent conventions](conventions.md#subagent-conventions) — a broad, shallow sweep across `SCOPE`. Categories the scanner looks for:

- **Unreachable code** — statements after unconditional `return`/`throw`/`break`, branches that can't be entered, conditions that are always true/false.
- **Orphaned exports** — exported symbols with zero importers anywhere in the repo.
- **Unused private symbols** — file-local functions, constants, types with no in-file references.
- **Unused imports** — imported names that aren't referenced in the file.
- **Orphaned files** — files with no importers anywhere in the repo.
- **Leftover commented-out code** — comment blocks that are clearly old code, not explanatory prose.

The scanner reports findings using the [Finding Record schema](conventions.md#finding-record-schema), with `category` set to one of the above. It omits the `Verdict` field — that's only added by the auditors in 3c.

**Confidence bias:** prompt the scanner to omit any finding it is less than ~80% confident is dead. A missed finding is caught on a later run; a confidently-claimed false positive wastes audit cycles.

**Fan-out cap before 3c.** If the broad scan returns more than ~30 findings, do not auto-fan-out to 30+ parallel auditors. Summarize the findings by category, surface to the user, and ask whether to proceed across the full set, scope to a subset, or run in batches.

## Step 3c — Deep audit (parallel, one subagent per finding)

For each finding from 3b, spawn an auditor subagent in parallel — narrow and deep on that single finding. **Cap parallel auditors at 10**; batch the remainder.

Each auditor runs two checks before returning a verdict.

### (A) Places to grep for hidden references

Even if the broad scanner reported zero importers, references can hide in places grep didn't reach. The auditor checks every one:

- **Dynamic dispatch** — grep for the symbol name as a string literal (lookup tables, `require(name)` / equivalent, reflective access, message handlers keyed by name).
- **Non-code references** — grep HTML, JSON, YAML, Markdown, templates, and config files for the symbol name or filename.
- **Re-exports** — is this symbol re-exported through a barrel/index file (e.g. `index.ts`, `mod.rs`, `__init__.py`, `lib.rs`) that itself *is* consumed?
- **Documentation references** — grep for the name in JSDoc `@see`, README, external docs.

### (B) Polarity rules — even if references exist, classify as not-dead when

References alone don't always mean the symbol is alive in the user's sense. These rules flip polarity in the other direction:

- **Public API surface** — exported from a package entry point or anything declared in `package.json` `exports`/`main`/`bin`, `Cargo.toml` `[lib]`/`[[bin]]`, equivalent for the ecosystem. External consumers may depend on it even if no in-repo file does.
- **Entry points** — CLI commands, `bin` scripts, plugin registrations, framework conventions (e.g. Next.js page files, route handlers, web-framework view functions, OCaml `dune` `executable` stanzas).
- **Test-only support code** — referenced only by tests, but the tests themselves are real and meaningful. The code exists to support legitimate test scenarios; deleting it deletes the test.

### Auditor return values

| Verdict          | Meaning                                                                                            |
|------------------|----------------------------------------------------------------------------------------------------|
| `confirmed-dead` | All (A) checks turned up nothing AND no (B) polarity rule applies. Includes a one-line justification. |
| `not-dead`       | A reference was found OR a polarity rule applies. Includes the specific reason.                    |
| `uncertain`      | The auditor cannot decide without more information. Includes a specific question for the user.     |

**Malformed or empty auditor output → treat as `uncertain`. Never default to `confirmed-dead` on missing data.**

## Step 3d — Removal

Maintain one named accumulator per outcome category across this step:

- `removed` — findings where the code was deleted and verification passed.
- `rejected` — findings the auditor classified `not-dead`.
- `reverted` — findings where the code was deleted but verification failed and the deletion was rolled back.
- `uncertain` — findings the auditor classified `uncertain`, plus any malformed-output cases.
- `coverageFollowups` — regions where dead code was removed but the surrounding region had no test coverage.

### Removal preconditions

Before removing any code:

1. **Verification tooling must exist.** If the [verification loop](conventions.md#verification-loop) finds no detected tooling, do not auto-remove. Move every `confirmed-dead` finding to `uncertain` and surface to the user — autonomous deletion against a project with no safety net requires explicit consent.
2. **User checkpoint.** Present the full list of `confirmed-dead` findings with their auditor justifications. Ask which to proceed with (all / some / none). Do not delete any code until approval is in. The pause mechanism depends on the harness (interactive prompt, return to caller, etc.) — what matters is that no removal happens without explicit consent.

### Verdict dispatch

| Verdict          | Action                                                                                                  |
|------------------|---------------------------------------------------------------------------------------------------------|
| `confirmed-dead` | Run the removal procedure below. Append to `removed`, `reverted`, or `coverageFollowups` based on outcome. |
| `not-dead`       | Append to `rejected` with the auditor's reason verbatim. Do not modify code.                            |
| `uncertain`      | Append to `uncertain` with the auditor's question verbatim. Do not modify code.                         |

### Removal procedure (for `confirmed-dead` only)

For each approved `confirmed-dead` finding, **sequentially**:

1. Remove the code (and any imports that become unused as a result).
2. Run the [verification loop](conventions.md#verification-loop). The loop reverts the change automatically on failure.
3. **If verification passed:** the removal stands.
   - Append to `removed`.
   - **Coverage check:** run `git grep -n "<symbol>"` (or the surrounding function/class name) scoped to the project's test paths (see [verification.md](verification.md) for common test-path conventions per ecosystem; ask the user if unclear). If no test path matches, append the region to `coverageFollowups`.
4. **If verification failed:** the loop already reverted.
   - Append to `reverted` with the failing check's name and message. The audit was wrong — something depends on this code that grep didn't catch.

## Step 3e — Report

Output a structured report keyed by the accumulators. If an accumulator is empty, write "none" — the section must still appear so nothing is silently dropped.

```
## Dead code cleanup report

### Removed ({count})
- {file:line} — {category}: {one-line description}

### Rejected by deep audit ({count})
- {file:line} — {category}: {auditor's reason verbatim}

### Reverted by failing verification ({count})
- {file:line} — {category}: {check that failed, message}

### Uncertain ({count})
- {file:line} — {category}: {auditor's question verbatim}

### Coverage follow-ups ({count})
- {file/region}: add tests — region was uncovered when dead code was removed.
```
