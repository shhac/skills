---
name: improve-code-structure
description: Analyzes and improves code structure — decomposes long functions and files, reduces complexity, extracts shared patterns, reframes complexity so whole branches or layers disappear, flags abstractions that don't fit (thin wrappers, over-generalization, reinvented helpers), assesses test coverage on critical paths, and cleans up dead, unreachable, or orphaned code that accumulates as a side effect of refactoring. Use when the user wants to refactor for clarity, split large files, reduce nesting, DRY up code, simplify an over-engineered or wrong-fit abstraction, replace a reinvented helper with the repo's canonical one, improve testability, or sweep for dead code after restructuring. Not for feature changes, bug fixes, or performance optimization — this is structural refactoring only.
---

# Improve Code Structure

Analyze code for structural improvements, then implement changes with user approval.

## Scope

- **Default:** entire repo (excluding vendored/generated code, node_modules, build output)
- **Narrowed:** if the user specifies a file, directory, or function — analyze that, but consider the surrounding context (a function lives in a file; a file lives in a module)
- When scoped to a specific function: analyze the whole file to understand context, then narrow recommendations to changes that affect the target function
- **Monorepos / large repos:** if the repo has multiple packages or services, ask the user to scope to a specific one rather than analyzing everything

---

## Instructions

You are the **lead** orchestrating a structural analysis and refactoring workflow.

For three worked examples of how the lead should behave end-to-end (full happy path, Phase 3 skipped because no changes were approved, and a revert-on-fail in Phase 3d), see [references/examples.md](references/examples.md).

Copy this checklist into your first response and tick items off as you progress. It is your authoritative progress record across all four phases:

```
- [ ] Phase 1a — spawn one analyst subagent per lens, in parallel (every lens in references/lenses.md, no skipping)
- [ ] Phase 1b — synthesize findings into a prioritized plan
- [ ] Phase 1c — present the plan and wait for user approval
- [ ] Phase 2a — record baseline ref before the first change
- [ ] Phase 2b — implement approved changes sequentially, verifying each
- [ ] Phase 3  — dead code detection & cleanup (skip if Phase 2 made no changes)
- [ ] Phase 4  — final verification + cross-phase summary
```

### Phase 1: Analysis

Spawn one subagent per lens listed in [references/lenses.md](references/lenses.md), in parallel. **Every lens must run** — count the lens sections in lenses.md and confirm you spawned that many subagents before continuing. Skipping a lens because it "seems unlikely to find anything" is not allowed; each lens covers a distinct failure mode and the value comes from running the full sweep. If a lens genuinely doesn't apply (e.g. the test-coverage lens against a project with zero tests), the analyst will report "no findings" — that's the correct outcome, not a reason to skip.

Each subagent receives:

- The lens content from lenses.md (one section, verbatim) as its role.
- The module-boundary note from the top of lenses.md (self-scoping; intra-module lenses can disregard it).
- The scope (full repo, directory, or file).
- The standard fields per [conventions.md](references/conventions.md#subagent-conventions).

Tell each analyst to focus on **impact** (the changes that genuinely improve clarity, testability, or maintainability — not every long function) and to note **dependencies** between findings (e.g. "splitting this function creates a new shared utility candidate"). Output uses the [Finding Record schema](references/conventions.md#finding-record-schema), without the `Verdict` field.

#### Synthesis

Once all analysts report:

1. Merge findings, resolving conflicts and dependencies:
   - A function split may create a file-split opportunity — link them
   - A pattern extraction may obviate a complexity reduction — note it
   - Don't recommend both splitting a function AND extracting its internals as a shared pattern — pick one
   - When a structural-simplification finding would delete code that another finding proposes to decompose, dedup, or polish, prefer the delete-finding and drop the rearrange-finding — don't present both for the same code
2. Order recommendations by impact and natural dependency (what enables what)
3. Present to the user as a prioritized plan:
   - Group by area of code, not by lens
   - For each recommendation: what to change, why, and what it enables
   - For any recommendation carrying a `Risk` note (restructurings that span files or remove a layer/abstraction), surface that blast radius alongside it — the user needs it to weigh ambition against risk at this gate
   - Flag any recommendations that are in tension with each other — let the user decide

**Present the prioritized plan and wait for approval** — the user picks which recommendations to implement (all, some, or none). Do not proceed past this point without explicit approval. The pause mechanism depends on the harness (interactive prompt, return to caller, etc.) — what matters is that no Phase 2 changes happen until approval is in.

### Phase 2: Implementation

The lead implements approved changes directly, in dependency order.

**Before the first change:** record the **baseline ref** by running `git rev-parse HEAD` and remembering the SHA. Phase 3a's scan scope depends on diffing against this exact ref, so it must be captured *before* any modifications. If the working tree is dirty at the start of Phase 2, ask the user to commit, stash, or explicitly accept that the existing changes will be folded into the baseline.

#### Invariants (must hold throughout Phase 2)

- **Preserve interfaces** — these are structural improvements, not feature changes. If tests exist, they should still pass (with imports/paths updated for new locations). If no tests exist, preserve the project's interfaces explicitly: exported symbols and their signatures, public file paths, and package entry points (`package.json` `exports`/`main`/`bin`, `Cargo.toml` `[lib]`/`[[bin]]`, the equivalent for the ecosystem in use). If a refactor would change any interface, surface it before making the change.
- **Don't gold-plate** — implement what was approved, nothing more. Don't "improve" surrounding code while you're in there.

#### Per-change loop

Sequentially, **one logical change at a time** — don't batch a file split, a function extraction, and a dedup into a single step; each should be independently verifiable. A structural-simplification change is still *one* logical change even when it spans several files or removes a layer — keep it atomic and verify it as a unit; don't split it into half-applied intermediate states, and don't pad it with unrelated cleanups. For each change:

1. Make the change. If it involves moves or renames, update all call sites — grep to verify nothing is missed.
2. Run the [verification loop](references/conventions.md#verification-loop).
3. Brief status update to the user.

### Phase 3: Dead Code Detection & Cleanup

After Phase 2 makes changes, dead code accumulates as a side effect — orphaned exports, unreachable branches, unused imports, files no one imports anymore.

**Skip if Phase 2 made no changes.** Otherwise, follow [references/dead-code-cleanup.md](references/dead-code-cleanup.md). The phase is a five-step pipeline:

- **3a — Scope:** files changed in Phase 2 (`git diff --name-only <baseline-ref>...HEAD`) plus their pre/post-refactor import neighbors.
- **3b — Broad scan:** one subagent sweeps the scope for six categories of dead code.
- **3c — Deep audit:** one parallel subagent per finding (cap 10) verifies the false-positive traps and returns `confirmed-dead` / `not-dead` / `uncertain`.
- **3d — Removal:** sequential, with preconditions (verification tooling exists; user approved the list) and per-removal verification revert-on-fail.
- **3e — Report:** structured summary covering removed, rejected, reverted, uncertain, and coverage follow-ups.

The full procedure — including the trap checklists, verdict dispatch table, named accumulators, and removal preconditions — is in references/dead-code-cleanup.md.

### Phase 4: Validation

After all approved changes and dead-code removals are complete:

1. Run the [verification loop](references/conventions.md#verification-loop) one final time across the whole project, not just changed files.
2. Summarize what was changed across all phases: files created/moved/split, functions extracted, patterns consolidated, dead code removed.
3. Note any analyst findings that were approved but deferred or skipped, and why
4. Surface the test-coverage follow-ups from Phase 3e as a recommended next step
