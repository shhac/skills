# Analyst lenses

Phase 1 spawns one subagent per lens. Each subagent receives one section of this file verbatim — that section *is* its role. Pass each lens together with the scope and the standard fields from [conventions.md](conventions.md#subagent-conventions). Output uses the [Finding Record schema](conventions.md#finding-record-schema).

**Every lens below must run on every Phase 1 invocation.** Adding a new lens is straightforward — append a numbered section. Removing or skipping a lens is not — each one covers a distinct failure mode that the others miss, so the value comes from running the full sweep. If a lens genuinely has nothing to report on a given codebase, its analyst returns an empty findings list, which is the correct outcome.

## A note on module boundaries

Pass this note to every analyst alongside its lens section. It is self-scoping — intra-module lenses can disregard it.

Most of these lenses operate *inside* a module — decomposing functions, flattening conditionals, deduping within a file. Those changes don't touch module boundaries and need no special care; decompose as granularly as clarity warrants. A few lenses do cross boundaries — extracting code to a shared location (file decomposition, pattern deduplication) and removing a layer (structural simplification). For those, one thing matters: don't add *accidental cross-module coupling*.

- **Reuse through interfaces, not internals.** When a change makes one module depend on another, route through its public interface. Don't introduce a new edge that deep-links into another module's internals to reach the shared code.
- **Don't scatter one import location into many across modules.** The concern is a consumer being forced to import a cohesive concept from several modules where it used to come from one. The reverse — *reducing* import locations by consolidating scattered code — is a win, not a regression.

These are all fine and need no second thought:

- Splitting `getFoo({x}|{y}|{z})` into `getFooByX/Y/Z` exported from the same entry point — the import location is unchanged and call sites get clearer and better-typed.
- Extracting genuinely shared library code consumed widely by callers that share a real concept — a healthy intentional hub.
- Consolidating scattered helpers into one module — fewer import locations.

If a finding hinges on *whether a boundary sits in the right place* rather than the code inside it, that's a boundary question — flag it and note it as out of scope for this pass.

## 1. Function decomposition

Find functions that are too long or handle multiple concerns. Look for:

- Functions doing more than one thing (setup + logic + cleanup, fetch + transform + render).
- Functions hard to test because they mix side effects with pure logic.
- Opportunities to extract testable pure functions from effectful code.

## 2. File decomposition

Find files that are too large (350+ lines as a guideline, not a hard rule). Look for:

- Files containing multiple unrelated concepts.
- Files where one section could serve a broader audience (belongs in a shared/common location).
- Whether new files should be siblings, a subdirectory, or relocated to a shared space.
- Note: decomposing a long function may increase a file's function count, creating new file-split opportunities — flag these.

## 3. Complexity reduction

Find unnecessarily complex code. Look for:

- Deep nesting that could be flattened with early returns or guard clauses.
- `let x; try { x = ... } catch { ... }` patterns (or the equivalent in this language) that should be extracted into functions.
- Complex conditionals that could be simplified by inverting, decomposing, or using lookup tables.
- Overly clever code that sacrifices readability for brevity.

## 4. Pattern deduplication

Find repeated patterns that should be shared. Look for:

- Near-identical code blocks across files (not just exact duplicates — similar structure with minor variation).
- Repeated error handling, validation, or transformation patterns.
- Opportunities for shared utilities, but only when 3+ call sites exist — don't abstract prematurely.

## 5. Test coverage on critical paths

Identify critical code and assess its test coverage. Look for:

- Code that handles money, auth, data mutations, or external integrations.
- Edge cases that aren't covered (nulls, empty collections, boundary values, concurrent access).
- Functions that were recently decomposed or simplified by other lenses and now need their own tests.
- If the project has no test infrastructure, still identify critical untested paths but note the gap.

## 6. Structural simplification ("code judo")

Find changes where a cleaner reframing could delete whole categories of complexity, rather than rearranging the same complexity into a tidier shape. Be ambitious: prefer the reframing that makes the change feel inevitable in hindsight over a safer rearrangement that preserves the original messy shape. Look for:

- A complicated implementation where a cleaner reframing could delete whole categories of complexity.
- A state model that could be reframed so conditionals disappear instead of getting centralized.
- A layer, mode, flag, or option that could be removed because the architecture already supports the behavior more directly — delete a whole layer of indirection rather than polishing it.
- Special-case logic that could collapse into a simpler default flow with fewer exceptions.
- Code that technically works but leaves the surrounding flow more tangled — prefer keeping the behavior and restructuring the implementation.

Constraints (this skill is behavior-preserving):

- Every finding must preserve observable behavior and public interfaces.
- For any finding that is a genuine restructuring rather than a local extraction, fill in the schema's `Risk` field with the blast radius: what it touches, what could break, why it's worth doing now, and the assumption you're making about why the existing complexity exists — so the user can weigh it at the approval gate.
- Prefer a few high-conviction "this whole thing could go away" findings over many speculative reframings.

## 7. Abstraction fit

Find abstractions that are the wrong shape, the wrong size, or already solved elsewhere in the codebase. Be ambitious about pushing the change onto the pattern the repo already uses rather than accepting a parallel one. Look for:

- Thin wrappers, identity functions, or pass-through helpers that add indirection without buying clarity.
- Premature or speculative generality — a generic mechanism serving a single caller, or "magic" handling that hides a simple, fixed data shape.
- Casts, optionality, or ad-hoc object shapes introduced to paper over an unclear invariant, where making the contract explicit would simplify the control flow.
- Bespoke helpers where the codebase already has a canonical utility for the job. Reinventing something the repo already solves is a strong signal the change is following the wrong pattern — prefer the canonical helper, and treat a near-duplicate as a prompt to ask whether the new code belongs in the established shape.
- Logic placed in the wrong layer for the concept it serves. (Stay local to the refactor scope — whole-repo boundary topology is the seam-audit skill's job.)
