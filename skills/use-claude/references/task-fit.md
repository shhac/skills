# What to delegate to Claude (and what to keep)

Evidence-based as of mid-2026 (Anthropic/OpenAI announcements, SWE-bench Pro / Terminal-Bench results, third-party head-to-heads from firecrawl/composio/zapier/catdoes). Directional, not gospel — validate against actual results and update this file when the picture shifts.

## Why delegate at all

- **Separate budget.** Claude Code spends an Anthropic subscription or API budget, not the caller's tokens. Offloading work shifts cost to a different pool entirely.
- **Quality-per-task, not token thrift.** Claude uses more tokens than token-economical competitors (head-to-heads measured ~3–4x more per task) but buys measurably more complete first-pass output — blind reviewers preferred Claude's code roughly 2:1 in published comparisons. Delegate to Claude when correctness and completeness dominate the cost calculus, not to save tokens.
- **A different model family catches different bugs.** Cross-family review is valuable in both directions.
- **Project-context awareness.** Claude Code auto-loads the repo's CLAUDE.md, settings, memory, and skills — a delegated task inherits project conventions without them being restated in the prompt.

## Good delegation targets

| Task | Why it fits |
|---|---|
| Well-specified but hard implementation | Claude leads SWE-bench Pro-style work: real-repo, multi-file changes where the first pass needs to be right. Write the spec (files, approach, acceptance criteria), then hand it over. |
| Long-horizon debugging | Tangled multi-file root causes, state-dependent bugs, regressions with unclear origin. |
| Test authoring | Thorough edge-case coverage is a completeness problem — Claude's strength. |
| Cross-family second opinion / adversarial review | Review a plan or diff; use a `VERDICT: APPROVED` / `VERDICT: REVISE` sentinel for loopable output. |
| Convention-sensitive repo work | Tasks where matching existing project style/tooling matters; Claude Code picks up CLAUDE.md automatically. |

## Not delegation targets

A headless `claude -p` call cannot interview the user. Work that is ambiguous, underspecified, or mid-architecture-discussion belongs to whoever holds the user conversation — delegating it headlessly (to any model) trades away the clarifying loop that makes it tractable. Reduce unknowns first; delegate the well-specified remainder.

Likewise keep cheap mechanical sweeps (bulk renames, migration boilerplate) with the caller if the caller is the more token-efficient model — paying Claude's token premium for work any model does correctly buys nothing.

## The core pattern

**Caller plans, Claude executes, caller verifies.** Package full context into the prompt (problem, constraints, files, acceptance criteria — plus anything the repo's CLAUDE.md won't already say), run with the target repo as cwd, then validate the result — run tests, review the diff — before trusting it. Treat Claude as a peer whose claims get checked, not an authority.

## Cost/limits notes

- Subscription plans (Pro/Max) meter usage in rolling windows with weekly caps; API-key usage bills at standard Anthropic API rates instead.
- Choose the model by task weight: `haiku` for lookups, `sonnet` for most delegated work, `opus`/`fable` for the hardest problems (top-tier model availability varies by plan).
- Even a trivial call carries ~7k input tokens of fixed overhead (more in a configured repo) — don't delegate one-liners answerable from context already in hand.
