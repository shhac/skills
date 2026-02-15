---
name: team-solve
description: Investigate and solve problems using a team of specialist agents. Use when facing complex, multi-faceted problems that benefit from parallel research and structured implementation. Decomposes problems into investigation tracks, runs parallel research, then implements solutions serially with fresh validation.
---

# Team Solve

Investigate and solve one or more problems using parallel research, then serial implementation.

## When to Use

- A task with multiple distinct problems or themes to address
- A codebase change that benefits from researching several areas at once
- Work that can be decomposed into independent investigation tracks
- Situations where you want structured evidence-gathering before making changes

## Workflow

1. **Decompose** — break the problem into 2-5 investigation tracks
2. **Investigate** — parallel teammates each research their track
3. **Discuss** — review findings with the user, revise approach if needed
4. **Implement** — investigators implement their changes, one at a time
5. **Validate** — fresh teammate verifies everything

---

## Instructions for Claude

You are the **team lead** orchestrating an investigate-then-solve workflow.

### Phase 1: Problem Decomposition

1. Parse the user's input to identify distinct problems or themes
2. If the problems are ambiguous or underspecified, ask clarifying questions before proceeding
3. Group related problems into 2-5 investigation tracks (one per teammate)
4. Present the decomposition to the user:
   - List each track with its assigned problems
   - Name each teammate descriptively (e.g., `filter-investigator`, `output-researcher`)
   - Ask: "I'll spin up N investigators in parallel. Proceed?"

### Phase 2: Parallel Investigation

Investigations run **in parallel** — this is where the team structure pays off.

1. Create a team with `TeamCreate`
2. Create tasks for each investigation track with `TaskCreate`
3. Spawn one `general-purpose` teammate per track using `Task` with `team_name`
   - Each teammate's prompt must include:
     - The specific problems to investigate
     - Instruction to **research only, do not make changes**
     - The subagent guidance below (copy it into their prompt)
     - Instruction to report findings via `SendMessage` using the report format below
   - **Spawn all investigators in parallel** — do not wait for one to finish before starting the next
4. **Do NOT shut down investigators when they report back** — they retain context for Phase 4

#### Subagent Guidance for Investigators

Include the following in each investigator's prompt:

> **Use subagents (`Task` tool) to keep your context focused.** Spawn subagents for:
> - Exploring specific files, modules, or subsystems
> - Searching through git history, logs, or large codebases
> - Any research tangent that might not pan out
>
> Each subagent should report back:
> 1. **Relevant findings** — what it discovered that matters to your investigation
> 2. **Red herrings** (1-2 sentences) — anything that *looks* related but *isn't*, and why. Calling these out early prevents wasted cycles re-exploring dead ends.
>
> After receiving a subagent's report, decide whether to:
> - **Use its findings directly** — if the summary gives you enough to proceed
> - **Dive in yourself** — if the subagent found something promising and you want full, first-hand context in that area before drawing conclusions

#### Investigator Report Format

Each investigator should structure their report as:

```
## Track: {description}

### Findings
- {what was discovered, root causes, relevant code paths}

### Proposed Approach
- {what to change, which files, how}

### Risks & Edge Cases
- {what could go wrong with this approach}
- {what adjacent code/features could be affected}
- {what happens if data is unexpected or flow is interrupted}

### Confidence: {high/medium/low}
{brief justification}

### Dependencies
- {does this approach depend on or conflict with other tracks?}
```

### Phase 3: Discussion Checkpoint

1. As investigators report back, give the user brief progress updates — don't wait silently for all of them
2. Once all investigators have reported, synthesize findings:
   - Key findings per track
   - Proposed approaches and confidence levels
   - Any conflicts or dependencies between tracks
   - **Ripple effects** — consider across all tracks:
     - *"What happens to..."* — documentation, adjacent features, API consumers, shared state, caching
     - *"What happens if..."* — unexpected data, interrupted flows, concurrent access, rollback
   - Recommended implementation order (dependencies first, then highest-risk, then the rest)
3. If investigation reveals the problem is different than expected, say so — propose revised tracks rather than forcing the original plan
4. Ask the user: "Ready to implement, or want to revise the approach?"

### Phase 4: Serial Implementation

Implementations happen **one track at a time**. This prevents:
- Mixed, unrelated work in a single commit
- Confusing build/test failures caused by concurrent changes in flight
- File conflicts when teammates touch shared code

1. For each track (in the order agreed with the user):
   - Message the original investigator to begin implementation via `SendMessage`
   - Assign their implementation task via `TaskUpdate`
   - Include the subagent guidance for implementation below in your message
   - **Wait for completion before starting the next track**
   - After each track completes, have the teammate report what changed
2. **Parallel exception**: Only consider parallel implementation if tracks have **zero file overlap** AND the codebase has no shared build/test pipeline that could produce confusing interleaved failures. If you think parallel is safe, explain why and ask the user.

#### Subagent Guidance for Implementation

Include the following when sending implementation instructions:

> **Use subagents for repetitive or mechanical edits.** If you need to make similar changes across many files (e.g., updating imports, renaming across test files, applying a pattern to multiple modules), spawn a subagent to handle batches. This keeps your main context focused on the implementation logic rather than filling up with repetitive diffs.

### Phase 5: Validation

1. Spawn a fresh `general-purpose` teammate named `validator` with instructions to:
   - Detect the project's test/lint/typecheck tooling and run appropriate checks
   - Review all changed files for correctness and consistency
   - Check that each problem from Phase 1 is actually addressed
   - Look for unintended side effects or regressions
   - Report pass/fail with details via `SendMessage`
2. If validation fails:
   - Route failures back to the responsible investigator for fixes
   - Re-run validation after fixes
3. Once validation passes, shut down all teammates and report results to the user

### Rules

- **Investigate in parallel, implement in series** — research benefits from parallelism; implementation benefits from sequencing
- **Subagents are cheap, context is expensive** — teammates should offload research tangents and repetitive edits to subagents rather than doing everything inline
- **Keep investigators alive** between phases — their context is valuable for implementation
- **3-5 teammates max** — if more problems than that, group into themes
- **Never `git add .`** — teammates must add specific files
- **Validator is always fresh** — do not reuse an investigator as validator
- If a teammate goes idle, that's normal — send them a message when it's their turn
