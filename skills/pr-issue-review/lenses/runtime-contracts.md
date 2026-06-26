# Runtime Contracts Lens

Use this lens when the PR touches API inputs/outputs, schemas, generated contracts, route or request parameters, configuration/env values, serialization, data mapping, framework lifecycle, or values crossing module/service boundaries.

Look for:

- Type assertions, casts, or unchecked conversions where runtime validation or guards are needed
- The same identifier/value shaped differently across read/write or caller/callee paths
- Inputs that drift from the documented, generated, or observed API/schema contract
- Request, route, config, or environment values used without checking their runtime shape
- Lifecycle or closure risks when callbacks, contexts, transactions, sessions, or handles can outlive the values they captured
- Deferred or concurrent work — promises, futures, async tasks, callbacks, goroutines, threads, or background jobs — started without being awaited, joined, or otherwise tracked, so a failure is swallowed or the work can be dropped before it completes
- Hand-rolled result shapes that can drift from canonical contracts
- Null/optional/error values that make invalid states easy to pass downstream

Good findings distinguish style from runtime risk. Prefer concrete contract evidence from schemas, generated types, docs, nearby guards, or established project patterns, then suggest the smallest safer shape.

When deferred work is left unawaited or unjoined, check whether that is deliberate. An intentional fire-and-forget with its own error handling or logging is a legitimate pattern, so call it out as context rather than a reason to withhold approval. Reserve a stronger finding for cases where a dropped or swallowed failure silently loses work the issue depends on.
