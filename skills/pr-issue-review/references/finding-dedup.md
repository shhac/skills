# Finding Dedup

Lenses and focus packs overlap on purpose: retries, idempotency, partial failure, contract drift, and naming can each be reached from several directions. Overlapping coverage is good; duplicated findings are not.

When more than one loaded lens or focus pack covers the same concrete scenario:

- Leave one finding, framed by the most specific lens or focus pack that covers it.
- Anchor it once: one inline comment per location. Do not restate the same finding from a second lens or repeat it in the top-level body beyond its index bullet.
- Give it one severity from the global P0-P4 scale, judged under the most specific frame.
- Credit the other lenses in `Focus checked` instead of duplicating the comment.

The same discipline applies across severity levels: if a scenario is one finding, it gets one severity, not a P1 framing inline and a P2 framing in the body.
