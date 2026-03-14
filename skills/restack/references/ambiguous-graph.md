# Ambiguous Graph

The script can't determine the stacking order for some branches because they fork from the same commit.

## Example

```
main:  ●── A ── B ── C
              \─── D ── E (foo/a)
              \─── F ── G ── H (foo/b)
```

Both `foo/a` and `foo/b` fork from commit A on main. Neither is an ancestor of the other. The script doesn't know if the intended stack is:

**Option 1:** `foo/a` → `foo/b` (foo/b should be on top of foo/a)
```
main → foo/a → foo/b
```

**Option 2:** `foo/b` → `foo/a` (foo/a should be on top of foo/b)
```
main → foo/b → foo/a
```

**Option 3:** Independent (both stack directly on main, no relationship)
```
main → foo/a
main → foo/b
```

## Disambiguation Heuristics

Before asking the user, the script checks:

1. **Ancestry:** If one branch's tip is an ancestor of the other, the relationship is clear (not actually ambiguous).
2. **Timestamp:** The branch whose first commit is earlier is likely the base layer.
3. **Commit count:** Fewer commits suggests a base layer (smaller change).

These are heuristics, not guarantees. When the script reports ambiguity, it includes these signals.

## Resolution

Present the options to the user with the heuristic signals. Once they choose, re-run with an explicit `--branches` list that encodes the intended order:

```bash
# If user says foo/a is the base:
python3 <script> restack --branches foo/a,foo/b
```

The graph builder respects the branch list order as a tiebreaker — when two branches are otherwise equivalent candidates, the one listed earlier is preferred as the parent.
