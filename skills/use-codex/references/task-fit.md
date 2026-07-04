# What to delegate to Codex (and what to keep)

Evidence-based as of mid-2026 (OpenAI announcements, Terminal-Bench/SWE-bench results, third-party head-to-heads from firecrawl/composio/zapier/catdoes, community skill prior art). Directional, not gospel — validate against actual results and update this file when the picture shifts.

## Why delegate at all

- **Separate budget.** Codex spends ChatGPT-plan quota (or OpenAI API credits), not Claude tokens. Offloading work shifts cost to a different pool entirely.
- **Token-economical models.** GPT-5.5 is trained for token-efficient reasoning (~40% fewer output tokens than 5.4 for the same task; the Codex lineage added adaptive thinking-time and context compaction). Third-party head-to-heads measured ~3–4x fewer tokens per task than Claude Code on comparable work.
- **Second, independent perspective.** A different model family catches different bugs. Empirically strong at spotting auth gaps, concurrency issues, schema drift, shell-quoting errors in review.

## Good delegation targets

| Task | Why it fits |
|---|---|
| Scoped repo Q&A / codebase exploration | Read-only, cheap, and the answer is all that matters. "Where is X handled?", "trace this flow", "summarize this subsystem's design". |
| Well-specified implementation | Codex is steady and instruction-faithful once architecture is decided and unknowns are reduced. Write the spec (files to touch, approach, acceptance criteria) first, then hand it over. |
| Mechanical edits at scale | Renames, API-migration sweeps, test-gated refactors — cheap tokens, low ambiguity. |
| Second-opinion / adversarial review | Strongest empirical niche. Review a plan or diff; use a `VERDICT: APPROVED` / `VERDICT: REVISE` sentinel for loopable output. |
| Stuck bugs | After 2+ failed attempts on the same problem, a different model's approach often breaks the loop. Package context: problem, architecture, what was tried, success criteria. |

## Keep in Claude

| Task | Why |
|---|---|
| Ambiguous or underspecified work | Codex drifts without tight instructions. Reduce unknowns first — that's Claude's job. |
| Architecture and decomposition | Claude is the better thinking partner for unfamiliar-codebase reasoning and design trade-offs (Claude leads SWE-bench Pro; Codex leads Terminal-Bench). |
| Long multi-turn efforts needing session memory | Codex reportedly loses architectural context over long sessions and truncates middle content of large tool outputs. |
| Anything conversational with the user | Codex's reports are terse; synthesis and communication stay here. |

## The core pattern

**Claude plans, Codex executes, Claude verifies.** Reduce known-unknowns (architecture discussion, spec, file list), delegate the well-specified remainder, then validate the result — run tests, review the diff — before trusting it. Treat Codex as a peer whose claims get checked, not an authority.

## Cost/limits notes

- ChatGPT-plan limits are 5-hour windows plus weekly caps, shared across local + cloud (Plus roughly 15–80 gpt-5.5 messages per window; Pro tiers 5–20x that). `gpt-5.4-mini` has ~4x the headroom.
- With `CODEX_API_KEY` set, usage bills at standard API rates (gpt-5.5: $5/$30 per 1M in/out) instead of plan quota.
- Even a trivial `codex exec` costs ~30k input tokens on Codex's side (system prompt + tools) — don't delegate one-liner questions Claude can answer from context already in hand.
