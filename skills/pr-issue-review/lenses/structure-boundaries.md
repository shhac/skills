# Structure And Boundaries Lens

Look for structural risks that affect whether the PR is a good solution.

Check:

- Whether the change follows existing abstractions and local architecture
- Whether it widens the blast radius more than the issue appears to require
- Whether it introduces accidental hubs, import cycles, or suspicious dependency direction
- Whether a new abstraction is too broad, too thin, or mismatched with surrounding patterns
- Whether a simpler local change would solve the same problem with less coupling

Do not perform a full `improve-code-structure` analysis or `seam-audit`. Surface only concrete structural risks relevant to this PR.
