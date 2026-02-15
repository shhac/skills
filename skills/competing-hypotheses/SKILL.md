---
name: competing-hypotheses
description: Debug problems by investigating multiple hypotheses in parallel. Use when you have a bug, unexpected behaviour, or mystery where the root cause is unclear. Spawns parallel investigator agents each pursuing a different theory, then compares evidence to identify the most likely cause and fix.
---

# Competing Hypotheses

Debug problems by racing multiple theories in parallel. Each investigator pursues a different hypothesis, gathers evidence, and reports back. The lead compares findings to identify the root cause.

## When to Use

- "I have no idea why this is broken"
- A bug that could have multiple root causes
- Unexpected behaviour with no obvious source
- Performance regressions with unclear origin
- Intermittent failures that are hard to reproduce

---

## Instructions for Claude

You are the **lead investigator** coordinating a parallel hypothesis investigation.

### Phase 1: Hypothesize

1. Understand the problem from the user's input:
   - What's the symptom? (error message, wrong output, unexpected behaviour)
   - When does it happen? (always, sometimes, after a recent change)
   - What's already been tried?
2. Generate 2-5 plausible hypotheses for the root cause
   - Each should be distinct and testable
   - Cover different areas (data, logic, infrastructure, external dependencies, timing)
3. Present the hypotheses to the user:
   - List each hypothesis with a brief rationale
   - Ask: "I'll spin up N investigators to pursue these in parallel. Proceed?"
   - Incorporate any hypotheses the user wants to add or remove

### Phase 2: Parallel Investigation

1. Create a team with `TeamCreate`
2. Create tasks for each hypothesis with `TaskCreate`
3. Spawn one `general-purpose` teammate per hypothesis using `Task` with `team_name`
   - Name them after their hypothesis (e.g., `race-condition-investigator`, `data-corruption-investigator`)
   - Each investigator's prompt should include:
     - The overall problem description
     - Their specific hypothesis to pursue
     - Instruction to **investigate only, do not make changes**
     - What evidence to look for (see Investigation Guide below)
     - Instruction to report findings via `SendMessage`
4. Spawn all investigators in parallel
5. As investigators report back, give the user brief progress updates — don't wait silently for all of them
6. If an investigator discovers a recent commit already resolved the issue, report the finding to the user and end early if they confirm it's fixed

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
> Report red herrings even when your main findings are conclusive — they prevent other agents from re-exploring the same dead ends.
>
> After receiving a subagent's report, decide whether to:
> - **Use its findings directly** — if the summary gives you enough to proceed
> - **Dive in yourself** — if the subagent found something promising and you want full, first-hand context in that area before drawing conclusions. Examples: conflicting evidence that needs direct examination, low confidence in the subagent's assessment, or complex state/flow where first-hand context matters.
>
> When choosing subagent types, prefer read-only or exploration-focused types for open-ended codebase searches, and full-capability types for targeted analysis or tasks that need write access.

### Investigation Guide

Each investigator should:

1. **Search for evidence** supporting their hypothesis
   - Read relevant code paths
   - Check logs, error messages, stack traces if available
   - Look at recent changes (git log, git diff) that could be related
   - Examine configuration, environment, data
2. **Search for counter-evidence** that would disprove their hypothesis
3. **Rate their confidence** based on what they found
4. **Report** using the output format below

### Investigator Output Format

```
## Hypothesis: {description}

### Evidence For
- {evidence point}: {where found, what it means}

### Evidence Against
- {evidence point}: {where found, what it means}

### Red Herrings
- {code paths or areas explored that looked related but weren't, and why}

### Confidence: {high/medium/low}

### Root Cause (if found)
{specific root cause, file, line, mechanism}

### Suggested Fix
{what to change and why}

### Open Questions
- {anything unresolved that could help narrow it down}
```

### Phase 3: Compare & Conclude

1. Once all investigators have reported, compare findings:
   - Which hypothesis has the strongest evidence?
   - Did any investigator find definitive proof?
   - Do findings from different investigators corroborate each other?
   - Are there open questions that could be quickly resolved?
   - **Compound bugs** — if multiple hypotheses are confirmed, present as a multi-root-cause scenario and propose fixing in dependency order (fix the cause that enables the others first)
2. Present the analysis to the user:
   - Rank hypotheses by evidence strength
   - Highlight the most likely root cause
   - Note any surprising findings or ruled-out theories
   - Recommend next steps (fix, further investigation, or targeted test)

### Phase 4: Fix (Optional)

Skip this phase if the user only wanted diagnosis, not a fix.

1. If the root cause is clear and the user wants to proceed:
   - Message the investigator who found it to implement the fix
   - They already have full context from their investigation
2. If the root cause is unclear:
   - Propose targeted experiments to disambiguate
   - Ask the user which direction to pursue
3. After any fix, spawn a fresh `validator` teammate to verify the fix addresses the original symptom. The validator's spawn prompt must include: the original symptom, the confirmed hypothesis/root cause, and what the fix was intended to do.
4. If validation fails, route the failure back to the investigator who implemented the fix for corrections, then re-validate

### Rules

- **Keep investigators alive** until the conclusion — they may need follow-up questions
- **2-5 hypotheses max** — too many dilutes focus
- **Investigators don't communicate** — they work independently to avoid confirmation bias
- **Evidence over intuition** — rank hypotheses by concrete evidence, not plausibility
- **Counter-evidence matters** — a hypothesis with strong counter-evidence should be deprioritized even if it seems likely
- **Shut down when done** — after validation passes, or after the user declines to fix, shut down all teammates and report results
