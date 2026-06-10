# Assertive Nitpicks Lens

This lens is intentionally opinionated. Use it when listed by the assertive or aggressive profile.

Look at changed lines and ask: "Would I be happier maintaining this code if this small thing were improved now?"

Leave inline comments for concrete improvements in:

- Names that could be more precise, conventional, shorter, or more domain-specific
- Branching that could be flatter, clearer, or split into guard clauses
- Functions that are long, return-heavy, or stateful enough to be annoying to reason about
- Files that are accumulating unrelated behavior or becoming harder to navigate
- Functions that mix concerns or hide testable logic inside IO/framework glue
- Tests that cover the implementation but not the behavior, or miss an obvious edge case
- Assertions that are too broad, too weak, or hard to diagnose when they fail
- Repeated literals, magic values, duplicated setup, or fixtures that obscure intent
- Error messages, log lines, and comments that are vague, misleading, or stale
- Type shapes, null handling, and optional values that make invalid states too easy
- Import choices, helper placement, and file organization that drift from nearby patterns

Prefer suggestion blocks when the fix is local and obvious. For subjective improvements, make the comment concise and phrase it as a quality suggestion, not a blocker.

Split nits by weight: use `💅 P3` when landing the fix would make the merged code a better example to follow, and `💭 P4` when it is a pure preference the author can take or leave.

Do not pad the review with generic praise. If there are no useful nits, say nothing from this lens.
