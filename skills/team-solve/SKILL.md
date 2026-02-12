---
name: team-solve
description: Investigate and solve problems using a team of specialist agents. Use when facing complex, multi-faceted problems that benefit from parallel research and structured implementation. Decomposes problems into investigation tracks, runs parallel research, then implements solutions serially with fresh validation.
---

# Team Solve

Investigate and solve one or more problems using parallel research, then serial implementation.

## Workflow

1. **Investigate** — parallel teammates each own a problem/theme
2. **Discuss** — review findings, revise scope if needed
3. **Implement** — investigators solve their own problems (serial by default)
4. **Validate** — fresh teammate verifies everything

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
   - Ask: "I'll spin up N investigators. Proceed?"

### Phase 2: Parallel Investigation

1. Create a team with `TeamCreate`
2. Create tasks for each investigation track with `TaskCreate`
3. Spawn one `general-purpose` teammate per track using `Task` with `team_name`
   - Each teammate's prompt should include:
     - The specific problems to investigate
     - Instruction to **research only, do not make changes**
     - Instruction to report findings via `SendMessage` using the format below
   - Spawn all investigators in parallel
4. **Do NOT shut down investigators when they report back** — they retain context for Phase 4

#### Investigator Report Format

Each investigator should structure their findings as:

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

1. Once all investigators have reported, synthesize findings for the user:
   - Key findings per track
   - Proposed approaches and confidence levels
   - Any conflicts or dependencies between tracks
   - **Ripple effects** — consider across all tracks:
     - *"What happens to..."* — documentation, adjacent features, API consumers, shared state, caching
     - *"What happens if..."* — unexpected data, interrupted flows, concurrent access, rollback
   - Whether implementation can be parallelized (total file separation) or must be serial
2. Ask the user: "Ready to implement, or want to revise the approach?"
3. Incorporate any feedback before proceeding

### Phase 4: Implementation

**Serial by default** to avoid file conflicts and git issues.

1. For each track, message the original investigator to begin implementation:
   - Assign their implementation task via `TaskUpdate`
   - Send implementation instructions via `SendMessage`
   - Wait for completion before starting the next track
2. **Parallel exception**: If tracks have **zero file overlap**, tell the user and ask if they want parallel implementation. If yes:
   - Remind teammates to use `git add <specific-files>` only
   - Each teammate owns distinct files — no shared edits
3. After each track completes, have the teammate report what changed

### Phase 5: Validation

1. Spawn a fresh `general-purpose` teammate named `validator` with instructions to:
   - Detect the project's test/lint/typecheck tooling and run appropriate checks
   - Review all changed files for correctness and consistency
   - Check that each problem from Phase 1 is actually solved
   - Report pass/fail with details via `SendMessage`
2. If validation fails:
   - Route failures back to the responsible investigator for fixes
   - Re-run validation after fixes
3. Once validation passes, shut down all teammates and report results to the user

### Rules

- **Keep investigators alive** between phases — their context is valuable
- **3-5 teammates max** — if more problems than that, group into themes
- **Never `git add .`** — teammates must add specific files
- **Validator is always fresh** — do not reuse an investigator as validator
- If a teammate goes idle, that's normal — send them a message when it's their turn
