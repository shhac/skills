---
name: seam-audit
description: Audit a codebase's module boundaries — enumerate modules, map their seams (import edges between modules), produce a layered topology diagram, and classify each module as narrow, hub-by-design, or accidental hub (with separate flags for cycles, layer violations, and uncertain import graphs). Outputs a diagram plus a flagged-for-review list; does not change code. Use when assessing whether abstractions live at the right boundaries, before/after a refactor to verify the boundaries improved, or when an unfamiliar codebase needs an architectural map. Not for intra-module refactoring (see improve-code-structure), bug hunting, or feature work.
---

# Seam Audit

Diagnostic pass over a codebase's *boundaries* — not the code inside modules, but the places where modules meet. The output is a map and a flagged list, never a change to the code.

## Vocabulary

The skill leans on three definitions. Use them explicitly when reporting:

- **Module** — a section of code with an interface and an implementation. Granularity is project-dependent: a file with exports, a folder of cohesive files, a published package, or a subsystem. Pick a granularity at the start of the run and hold it constant for the whole audit — mid-run re-classification breaks the diagram.
- **Seam** — an import edge between modules. `A` has an outgoing seam to `B` iff `A` imports `B`. `B`'s incoming seam from `A` is the same edge viewed from the other side. Static `import` / `require` / `use` is the default surface; tricky cases (dynamic imports, DI, framework routing) are covered in `references/import-graph-traps.md`.
- **Hub** — a module with many seams. Being a hub is not inherently bad: foundational types and orchestrators are hubs by design. The diagnostic question is whether each hub is *intentional*.

## Scope

- **Default:** entire repo. Step 1 below decides the module granularity; the user is asked only when the default rules are ambiguous.
- **Narrowed:** if the user names a specific subtree (e.g. "audit the auth subsystem"), enumerate modules within that subtree. Modules outside the subtree are *external* — count seams to/from them but don't classify them.
- **Monorepos and large repos (>~50 modules at the chosen granularity):** ask the user to scope to one package, service, or subsystem before running. A repo-wide topology at file-level granularity is rarely informative.
- **Excluded** by default: vendored code, generated code, build output, third-party packages, test files (the unit-of-audit is the production module; tests don't count toward incoming seams).
- **Too-small input:** if there are fewer than ~5 modules at any granularity, this skill is the wrong tool. Suggest a regular code review instead.

The skill emits no file changes. If the audit's findings should be acted on, hand off to a refactor skill (e.g. `improve-code-structure`).

---

## Procedure

Four steps. Each produces an artifact the next consumes. Total length: typically 10-50 modules' worth of analysis, deliverable in one response.

The agent running the skill MAY parallelize step 2 if its platform supports concurrent file reads or grep. The procedure does not depend on parallelism — sequential execution is equivalent in correctness, only slower.

### Step 1 — Define the unit of analysis

Decide what counts as a module for this run. In priority order:

1. If the user specified one (e.g. "treat each file as a module"), use that.
2. If the repo has obvious subsystem boundaries (a `src/` divided by purpose: `src/auth/`, `src/payments/`, etc.), default to those subsystems.
3. Otherwise, default to **each leaf file with public exports** — the most fine-grained interpretation.

If the chosen granularity produces more than ~50 modules, pause and ask the user to scope down (per the monorepo rule above).

Whatever you pick, state it explicitly in the first sentence of the report: *"For this audit, a module is N."*

### Step 2 — Enumerate modules + their seams

For each module in scope:

1. **Identify the interface.** What does this module export? Public symbols, files, package entry points — depending on the granularity from step 1. Language-dependent: TypeScript `export`, Python `__all__` / underscore convention, Go capitalized names, Rust `pub`, Java public classes, etc.
2. **Identify outgoing seams.** What does this module import from outside its boundary? Count distinct importees, not distinct symbols (`import { a, b } from "x"` = one seam to `x`, not two). Each external package counts as one outgoing seam (so `import a from "react"` + `import b from "lodash"` = two outgoing seams, displayed in the diagram and table collapsed under `external:*`).
3. **Identify incoming seams.** What in-scope modules import this module's interface? Same counting rule. Test files do not count.

How to gather this:

- For source languages with explicit `import` / `require` / `use` syntax: grep across the scope.
- For languages with implicit dependencies or any of the trap patterns in `references/import-graph-traps.md` (dynamic imports, DI, framework routing, barrel re-exports, plugin systems, string-based resolvers): apply the rubric in that file. If the traces aren't determinable, flag the affected modules with `uncertain-import-graph` and add a `Limitations` line to the report.
- External dependencies don't enter the classification table — only in-scope modules are classified — but their counts still contribute to the module's outgoing seam total.

Record per module: `{ name, role, outgoing-seams[list-of-names], incoming-seams[list-of-names], out-count, in-count, notes }`.

### Step 3 — Diagram the topology

Produce a **layered ASCII diagram** following one explicit arrow convention:

> **`A → B` means `A imports B`.**
> Place callers / entry surfaces at the top. Place foundations / dependencies at the bottom. Most arrows point *downward*.

Layer rule (plain language):

> Dependencies should point downward toward more foundational modules. An import that points *upward* (a foundational module importing an application module) is a `layer-violation` flag.

Cycles:

> Draw small cycles (≤4 modules) inline: `A → B → C → A`. Collapse larger cycles as a labeled node (`cycle group: A/B/C/D`) and list the full path in the flagged-list entry.

Cross-cuts (modules consumed across many layers — types, design system, foundational helpers):

> Draw as a separate band at the bottom or as labeled side-gutter arrows. Don't thread them through the main vertical flow.

The diagram is the most useful artifact this skill produces — invest in making it readable. If it doesn't fit on a single screen, either summarize (collapse layers into groups) or pause and ask the user to narrow scope. **Do not silently narrow scope mid-run.**

Full diagram conventions + a sample skeleton: `references/output-format.md`.

### Step 4 — Classify and flag

Each module gets **one classification + zero or more flags**. These are two independent axes — a module can be `hub-by-design` AND in a `cycle`.

Classifications (pick exactly one):

- **narrow** — 0-2 seams in each direction. Leaf utility, pure data, single-consumer adapter.
- **hub-by-design** — high seam count, but the role explains it: foundational types (consumed everywhere), composition roots (compose everything), orchestrators (drive many consumers), public-API barrel files. State the role explicitly in the table.
- **accidental hub** — high seam count that the role *does not* obviously explain. This is the finding the skill exists to produce.

Flags (zero or more, additive):

- `cycle` — module is part of an import cycle.
- `layer-violation` — module imports upward.
- `external-heavy` — most outgoing seams target external packages, not in-scope modules.
- `uncertain-import-graph` — static analysis is incomplete for this module (see `references/import-graph-traps.md`). The classification is best-effort.

Thresholds depend on granularity and project idioms. Pick a cutoff for the run and **state it in the report**:

- File-level: typically `outgoing >5` or `incoming >10` is a candidate for the hub bucket.
- Subsystem-level: typically `outgoing >3` or `incoming >6`.

Adjust to outliers *for this codebase*. The skill's job is the flagging; the fix lives in a refactor skill.

---

## Output

Single report with the sections specified in `references/output-format.md` § Required sections, in order:

1. Module-definition line
2. Threshold-disclosure line
3. Limitations line (only if applicable)
4. The diagram
5. The classification table (exact column schema in `references/output-format.md`)
6. Flagged for review — modules with `accidental hub` classification OR any flag besides `external-heavy`. Each entry: 1-2 sentences explaining *why* it's flagged + a **direction** for follow-up (not an implementation plan).
7. Not actioned (bounded) — modules considered borderline but not flagged. Keep to ~5 entries.

If there's nothing flagged: *"The boundaries are intentional — nothing flagged."* That's the most useful possible outcome.

Follow-up direction examples:

- ✅ *"Investigate splitting time helpers from string helpers — they share nothing semantically."*
- ❌ *"Move `dateAdd` and `dateSubtract` into a new file `time-helpers.ts`, update imports in foo.ts and bar.ts, …"* — that's a refactor plan; hand off to `improve-code-structure` instead.

---

## Anti-patterns to avoid

- **Don't over-decompose.** A module with one outgoing + one incoming seam isn't a virtue if the surrounding code is contorted to route through it. Flag genuine boundary issues, not architectural purity.
- **Don't moralize about hubs.** Foundational types are hubs *because* they should be foundational. The interesting finding is "this hub is accidental," not "this module has high fan-in."
- **Don't propose fixes inside this skill.** Direction-level suggestions only. Detailed refactor plans belong in a downstream skill.
- **Don't silently narrow scope.** If the diagram won't fit, summarize OR ask the user — don't drop modules to make it pretty.
- **Don't audit beyond the scope.** External dependencies are one seam each per importer. Per-method or per-symbol coupling is out of scope unless explicitly requested.
- **Don't run on a codebase with no clear module concept.** A single-file script or a flat directory of unrelated scripts doesn't need a seam audit.
- **Don't mistake static imports for the whole picture.** Read `references/import-graph-traps.md` before reporting — DI / dynamic imports / framework routing can hide significant seams.

---

## When to invoke this skill

- After a structural refactor — verify boundaries actually improved.
- Before scaling a subsystem — see where the seams cluster.
- When a new contributor needs an architectural map.
- When code review keeps surfacing "this change touched too many files" — usually a hub-by-accident.
- When import-direction cycles are suspected.

## When not to invoke this skill

- Bug investigation — wrong tool; use a debugger or a competing-hypotheses pass.
- Single-file improvements — wrong granularity; use a code review skill.
- "Make this faster" — wrong question; use a profiler.
- Active refactoring — this is diagnostic only. Pair it with `improve-code-structure` if changes are desired.

