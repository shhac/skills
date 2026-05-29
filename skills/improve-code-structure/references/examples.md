# Examples

Three worked examples covering the most common branches through this skill. Read these to model the lead's behavior — what to spawn, what to surface, when to pause, what the user sees at each handoff.

---

## Example 1 — Full happy path

**User request:** "Please improve the structure of this codebase."

**Phase 1 — Analysis.** The lead copies the progress checklist, marks Phase 1a in progress, and spawns one subagent per lens from [lenses.md](lenses.md), in parallel, with `scope = entire repo`. Each subagent gets the standard fields per [conventions.md](conventions.md#subagent-conventions) and outputs the [Finding Record schema](conventions.md#finding-record-schema).

The lead receives N reports, synthesizes them into a prioritized plan grouped by area of code (not by lens), flags two recommendations in tension with each other, and presents the plan. The plan looks like:

```
## Recommendations (prioritized)

### Area: src/payments/
1. **[high]** Split src/payments/processor.ts (842 lines) into orchestrator + adapters
   - Risk: touches every importer of processor.ts (~9 files) for the new paths; assumes the adapter boundary matches the existing payment-method split. Interfaces preserved.
   ...
2. **[high]** Extract shared validation helpers used in 4 call sites
   ...

### Area: src/auth/
3. **[medium]** Decompose src/auth/login.ts:loginHandler — currently mixes I/O, business logic, and response formatting
   ...

### Tensions
- (1) and (2) overlap on src/payments/validation.ts — recommend doing (1) first then (2).
```

The lead pauses for approval. *(In Claude Code that's an interactive prompt; in a headless harness it's a return-to-caller. The skill doesn't care which, only that no Phase 2 changes happen until approval is in.)*

**User approves all.**

**Phase 2 — Implementation.** The lead runs `git rev-parse HEAD` → records `a3f7c21` as the baseline ref. Then implements recommendations sequentially: makes change → runs the [verification loop](conventions.md#verification-loop) → posts a brief status. After each: tests, typecheck, lint all green. Three changes land cleanly.

**Phase 3 — Dead code cleanup.** Phase 2 made changes, so the phase runs. Per [dead-code-cleanup.md](dead-code-cleanup.md):

- *3a:* `git diff --name-only a3f7c21...HEAD` returns 7 changed files. The lead unions with their pre/post-refactor import neighbors → `SCOPE = 18 files`.
- *3b:* Spawns one broad-scan subagent. Returns 6 findings.
- *3c:* 6 ≤ 10, so spawns 6 deep auditors in parallel. Verdicts: 4 `confirmed-dead`, 1 `not-dead` (re-export consumed via barrel file), 1 `uncertain` (auditor: "is this referenced from the Storybook config?").
- *3d:* Verification tooling exists (npm scripts). Lead presents the 4 `confirmed-dead` findings with auditor justifications and asks all/some/none. **User approves 3 of 4** (skips one they want to keep for now). Lead removes them sequentially. 2 pass verification; 1 fails (an integration test depended on the function via a string lookup the audit missed) — the verification loop reverts that one removal automatically.
- *3e:* Report covers every accumulator.

**Phase 4 — Validation.** Final verification loop run across the whole project — green. The lead summarizes: 3 refactors landed, 2 dead-code removals landed, 1 reverted, 1 not-dead, 1 uncertain pending user decision, 1 coverage follow-up recommended.

---

## Example 2 — Phase 3 skipped (no changes approved)

**User request:** "Take a look at src/auth.ts and tell me what could be improved structurally."

**Phase 1.** Lead spawns analyst subagents with `scope = src/auth.ts` (and surrounding context per the Scope rules). Three recommendations come back. The lead presents the plan.

**User says:** "Thanks, just wanted to see the analysis. Don't change anything for now."

**Phase 2.** No changes implemented. The lead does *not* record a baseline ref because no implementation is happening.

**Phase 3.** Skip condition triggered (Phase 2 made no changes). The lead does not spawn the broad scanner; it does not compute a scan scope. It logs "Phase 3 skipped: no changes were made in Phase 2" and moves on.

**Phase 4.** No changes to validate. The lead summarizes: "Analysis only. 3 recommendations surfaced; none implemented per user request. The recommendations are above if you want to revisit."

The key point: **Phase 3 is downstream of Phase 2 changes.** No changes → no orphans introduced → nothing to scan for. Running the dead-code phase against an unchanged repo would just surface pre-existing dead code, which is a different task than this skill's goal.

---

## Example 3 — Revert on failed verification

**Setup:** Phase 3d is in progress. The auditor returned `confirmed-dead` for `formatLegacyDate(d: string)` in `src/utils/dates.ts:142`, with justification "no callers found in repo, no string-literal references, not in package exports."

**User has approved removal.** The lead proceeds.

1. Removes the function and its now-unused import of `parseISO`.
2. Runs the [verification loop](conventions.md#verification-loop): `npm test` → ❌ failing test:
   ```
   FAIL  src/orders/legacy-import.test.ts
     ✗ accepts ISO-8601 date strings from the legacy import path
       TypeError: formatLegacyDate is not a function
   ```
3. The verification loop reverts the change automatically (restores `formatLegacyDate` and the import).
4. The lead appends the finding to the `reverted` accumulator with the failing test name and message. **The audit was wrong** — `formatLegacyDate` was reached through a path the auditor's grep didn't catch (likely a re-import in a non-obvious file or a dynamic-dispatch call site that didn't match the symbol-name string search).
5. The lead continues to the next `confirmed-dead` finding.

**At Phase 3e**, the report's "Reverted by failing verification" section names this finding, the test that failed, and the message — so the user can investigate and decide whether to manually clean it up later.

The revert is deliberately *single-finding* — it does not cascade to other in-progress removals, because each removal is verified independently. The lead does not give up on Phase 3 after one revert; it continues through the remaining findings.
