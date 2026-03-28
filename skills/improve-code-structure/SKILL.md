---
name: improve-code-structure
description: Analyze and improve code structure — decompose long functions and files, reduce complexity, extract shared patterns, and assess test coverage on critical paths. Use when the user wants to refactor for clarity, split large files, reduce nesting, DRY up code, or improve testability. Not for feature changes, bug fixes, or performance optimization — this is structural refactoring only.
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

### Phase 1: Analysis

Spawn each analyst as a `Task` subagent (fire-and-forget — analysts aren't needed after reporting). Run all 5 in parallel.

#### Analyst Lenses

1. **Function decomposition** — Find functions that are too long or handle multiple concerns. Look for:
   - Functions doing more than one thing (setup + logic + cleanup, fetch + transform + render)
   - Functions that are hard to test because they mix side effects with pure logic
   - Opportunities to extract testable pure functions from effectful code

2. **File decomposition** — Find files that are too large (350+ lines as a guideline, not a hard rule). Look for:
   - Files containing multiple unrelated concepts
   - Files where one section could serve a broader audience (belongs in a shared/common location)
   - Whether new files should be siblings, a subdirectory, or relocated to a shared space
   - Note: function decomposition may increase a file's function count, creating new file-split opportunities — flag these

3. **Complexity reduction** — Find unnecessarily complex code. Look for:
   - Deep nesting that could be flattened with early returns or guard clauses
   - `let x; try { x = ... } catch { ... }` patterns that should be extracted into functions
   - Complex conditionals that could be simplified by inverting, decomposing, or using lookup tables
   - Overly clever code that sacrifices readability for brevity

4. **Pattern deduplication** — Find repeated patterns that should be shared. Look for:
   - Near-identical code blocks across files (not just exact duplicates — similar structure with minor variation)
   - Repeated error handling, validation, or transformation patterns
   - Opportunities for shared utilities, but only when 3+ call sites exist — don't abstract prematurely

5. **Test coverage on critical paths** — Identify critical code and assess its test coverage. Look for:
   - Code that handles money, auth, data mutations, or external integrations
   - Edge cases that aren't covered (nulls, empty collections, boundary values, concurrent access)
   - Functions that were recently decomposed (by lenses 1-3) and now need their own tests
   - If the project has no test infrastructure, still identify critical untested paths but note the gap

#### Analyst Instructions

Each analyst prompt should include:
- Their lens description (from above)
- The scope (full repo, directory, or file)
- Instruction to report findings as a prioritized list with file paths, line numbers, and concrete suggestions
- Instruction to focus on **impact** — don't flag every 50-line function, focus on the ones where splitting genuinely improves clarity or testability
- Instruction to note dependencies between their findings (e.g., "splitting this function creates a new shared utility candidate")

#### Analyst Output Format

```
## {Lens} Analysis

### Findings (prioritized)
1. **[impact: high/medium/low]** **{file:line}** — {what's wrong and why it matters}
   - Suggestion: {concrete recommendation}
   - Improves: {testability, readability, reuse, maintainability}
   - Dependencies: {other findings this interacts with, if any}

### Summary
{1-2 sentences: overall assessment from this lens}
```

#### Synthesis

Once all analysts report:

1. Merge findings, resolving conflicts and dependencies:
   - A function split may create a file-split opportunity — link them
   - A pattern extraction may obviate a complexity reduction — note it
   - Don't recommend both splitting a function AND extracting its internals as a shared pattern — pick one
2. Order recommendations by impact and natural dependency (what enables what)
3. Present to the user as a prioritized plan:
   - Group by area of code, not by lens
   - For each recommendation: what to change, why, and what it enables
   - Flag any recommendations that are in tension with each other — let the user decide

**Ask the user which recommendations to implement** (all, some, or none). Do not proceed without approval.

### Phase 2: Implementation

The lead implements approved changes directly — **sequentially**, one recommendation at a time, in dependency order.

For each change:
1. Make the change
2. Verify it works — detect the project's verification tooling (tests, typecheck, lint) and run what exists. Not all projects have all three.
3. If verification fails, fix the issue. If the fix isn't straightforward, revert and discuss with the user before moving on.
4. Brief status update to the user

#### Implementation Rules

- **Preserve behavior** — these are structural improvements, not feature changes. If tests exist, they should still pass (updated for new file/function locations). If no tests exist, don't change observable behavior.
- **Update imports and references** — when moving or renaming, update all call sites. Grep to verify nothing is missed.
- **Don't gold-plate** — implement what was approved, nothing more. Don't "improve" surrounding code while you're in there.
- **One logical change at a time** — don't batch a file split, a function extraction, and a dedup into a single step. Each should be independently verifiable.

### Phase 3: Validation

After all approved changes are implemented:

1. Run the full verification suite (tests, typecheck, lint) one final time
2. Summarize what was changed: files created, moved, split; functions extracted; patterns consolidated
3. Note any analyst findings that were approved but deferred or skipped, and why
