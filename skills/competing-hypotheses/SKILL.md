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
   - Cover different layers (data, logic, infrastructure, external dependencies, timing)
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
2. Present the analysis to the user:
   - Rank hypotheses by evidence strength
   - Highlight the most likely root cause
   - Note any surprising findings or ruled-out theories
   - Recommend next steps (fix, further investigation, or targeted test)

### Phase 4: Fix (Optional)

1. If the root cause is clear and the user wants to proceed:
   - Message the investigator who found it to implement the fix
   - They already have full context from their investigation
2. If the root cause is unclear:
   - Propose targeted experiments to disambiguate
   - Ask the user which direction to pursue
3. After any fix, spawn a fresh `validator` teammate to verify the fix addresses the original symptom

### Rules

- **Keep investigators alive** until the conclusion — they may need follow-up questions
- **2-5 hypotheses max** — too many dilutes focus
- **Investigators don't communicate** — they work independently to avoid confirmation bias
- **Evidence over intuition** — rank hypotheses by concrete evidence, not plausibility
- **Counter-evidence matters** — a hypothesis with strong counter-evidence should be deprioritized even if it seems likely
