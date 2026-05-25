# Output Format

The report two different agents produce for the same repo should be comparable. This file pins the exact format so they line up.

## Required sections (in this order)

1. **Module-definition line** — one sentence: *"For this audit, a module is N."* (Example: "a leaf TypeScript file with at least one named export.")
2. **Threshold-disclosure line** — one sentence stating the high-seam cutoffs *used for this run*. Example: *"Thresholds for this run: outgoing >5 or incoming >10 is a candidate for hub classification."* Without this, "high seam count" is unverifiable.
3. **Limitations line** *(only if applicable)* — one sentence calling out any import-graph blind spots. Example: *"Static-import analysis only; dynamic `import()` / DI container / route registration / autoload are not traced. Modules likely affected are flagged with `uncertain-import-graph`."* If you have full confidence, omit the line.
4. **The diagram** — ASCII, per `output-format.md` § Diagram conventions below.
5. **The classification table** — full table, every in-scope module, columns per § Classification table below.
6. **Flagged for review** — only modules with `accidental hub` classification, OR any flag that's not `external-heavy` (cycles, layer violations, and uncertain-import-graph all merit a flagged-list entry, even if the classification itself is narrow/hub-by-design).
7. **Not actioned (bounded)** — modules the audit considered borderline but decided not to flag. Lets reviewers sanity-check the verdicts. Keep to ~5 entries; if longer, the threshold is probably wrong.

If the audit finds **nothing flagged**, say so plainly: *"The boundaries are intentional — nothing flagged."* That's the most useful possible outcome.

## Diagram conventions

The diagram is ASCII, layered, and follows one explicit arrow convention:

> **`A → B` means `A imports B`.**
> Place callers / entry surfaces at the top. Place foundations / dependencies at the bottom. Most arrows point *downward*.

Layer rule (plain language, no math):

> Dependencies should point downward toward more foundational modules. An import that points *upward* (a foundational module importing an application module) is a `layer-violation` flag.

Cycle convention:

> Draw cycles inline when small (3-4 modules): `A → B → C → A`. Collapse larger cycles as a labeled node (`cycle group: A/B/C/D`) and expand the full path in the flagged-list entry.

Cross-cuts (modules consumed across many layers — types, design system, assert-unreachable helpers):

> Draw as a separate band at the bottom or as labeled side-gutter arrows. Don't try to thread them through the main vertical flow.

Sample skeleton (substitute the boxes with the actual modules):

```
┌─────────────────────────────────────────────┐
│ ENTRY SURFACES                              │
│  ┌────────────┐    ┌──────────────────┐     │
│  │ web        │    │ background-job   │     │
│  └─────┬──────┘    └────────┬─────────┘     │
└────────┼────────────────────┼───────────────┘
         │ A imports B        │
         ▼                    ▼
┌─────────────────────────────────────────────┐
│ COMPOSITION                                  │
│  ┌────┴──────────────────────┴─────────┐    │
│  │ route-handlers / orchestrator       │    │
│  └────────────────────┬────────────────┘    │
└──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ FOUNDATIONS (cross-cuts, consumed widely)    │
│  ┌────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ types  │ │ utils    │ │ design-system  │ │
│  └────────┘ └──────────┘ └────────────────┘ │
└─────────────────────────────────────────────┘
```

## Classification table

Two-axis verdict: **one classification + zero or more flags.**

Classifications (pick exactly one):

- `narrow` — 0-2 seams in each direction. Leaf utility, pure data, single-consumer adapter. Cheap to test, cheap to replace.
- `hub-by-design` — high seam count, but the role explains it: foundational types (consumed everywhere), composition roots (compose everything), orchestrators (drive many consumers). Mark explicitly as intentional.
- `accidental hub` — high seam count that the role *does not* obviously explain. This is the finding the skill exists to produce. Common causes:
  - Module grew over time from one purpose to many.
  - Dumping ground for shared helpers that don't belong together.
  - Mixes data and behavior that could split.
  - Crosses layer boundaries unnecessarily.

Flags (zero or more, additive to the classification):

- `cycle` — module is part of an import cycle. Always flag, regardless of classification.
- `layer-violation` — module imports upward (lower/foundational layer imports a higher/application layer).
- `external-heavy` — most outgoing seams target external packages, not in-scope modules. Useful signal for vendor lock-in or wrapper-layer candidates; not an issue on its own.
- `uncertain-import-graph` — static analysis is incomplete for this module's imports (dynamic import, DI, autoload, framework routes — see `import-graph-traps.md`). The classification is best-effort.

### Required columns

| Module | Role | Outgoing to | Incoming from | Out | In | Classification | Flags | Notes |
|---|---|---|---|---|---|---|---|---|

Per-column guidance:

- **Module** — the module identifier per the granularity stated in section 1.
- **Role** — 2-5 word phrase capturing the module's purpose. Helps justify a `hub-by-design` verdict.
- **Outgoing to** — the actual module names imported, comma-separated. External packages collapse under `external:*`. Truncate at ~5 names with `… +N more` if longer.
- **Incoming from** — same shape, listing in-scope importers.
- **Out** / **In** — integer counts. Out counts external packages individually; In does not include test files (tests are excluded from the audit per scope).
- **Classification** — exactly one of the three values above.
- **Flags** — comma-separated list of zero or more flag tokens.
- **Notes** — one short clause. Optional.

### Sample row

```md
| `compile-service/normalize` | Per-language normalize + hash | `compile-service/hash`, `external:*` | `sw-handler`, `prebake` | 2 | 2 | narrow | | Pure functions, fully tested |
| `runtime/index` | Lazy worker singletons | `yaegi-worker`, `zig-worker`, `rust-worker`, `comlink` | `use-runtime-run` | 4 | 1 | hub-by-design | | One row per language is unavoidable |
| `lib/legacy-helpers` | Mixed util grab-bag | 8 in-scope + `external:*` | 14 in-scope | 9 | 14 | accidental hub | | Split: time helpers vs. string helpers vs. validation |
```

### Flagged-for-review entries

For each flagged module, write 1-2 sentences:

1. **Why it's flagged.** Reference the specific seam pattern (e.g. "imports 9 in-scope modules across 4 layers" or "appears in cycle A→B→C→A").
2. **Follow-up direction.** Keep it at the level of direction, **not** an implementation plan. Examples:
   - *Good:* "Investigate splitting time helpers from string helpers — they share nothing semantically."
   - *Bad:* "Move `dateAdd` and `dateSubtract` into a new file `time-helpers.ts`, update imports in foo.ts and bar.ts, then…"

Follow-up is a hand-off cue for a refactor skill or a code review. The seam audit's job is locating the boundary issue, not drafting the fix.

