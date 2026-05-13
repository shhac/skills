# quotespeak scripts

Helper scripts for maintaining the `skills/quotespeak/references/quotes/` bank (theme/mood YAML leaves under per-theme directories, plus a `_universal/` cross-cutting layer).

## Requirements

Scripts depend on [PyYAML](https://pyyaml.org/). Pick whichever setup you prefer:

**Option A - `uv` (no setup, recommended):**

```bash
uv run --with pyyaml scripts/quotespeak/validate.py
```

**Option B - virtualenv:**

```bash
python3 -m venv .venv
.venv/bin/pip install pyyaml
.venv/bin/python scripts/quotespeak/validate.py
```

**Option C - system pip (macOS users may need `--break-system-packages`):**

```bash
pip install --user pyyaml
python3 scripts/quotespeak/validate.py
```

If PyYAML isn't installed, the script exits with code `2`.

## Scripts

### `validate.py` (read-only)

Checks the bank's structural invariants:

- Every theme directory has a `_vibe.md` and only the moods declared in the matrix have `<mood>.yaml` files.
- Each `_vibe.md`'s "Available moods" list matches the `.yaml` files in its directory.
- Every leaf YAML parses, has a non-empty `vibe:` field, and at least 5 quotes (target 8).
- No quote text appears in both `_universal/<mood>.yaml` and a theme leaf (cross-leaf dedup).
- `_universal/<mood>.yaml` counts stay under their per-mood cap (30 for most moods, 200 for `deadpan` which is the genuine cross-cutting catchall).

Reports every issue. Exits non-zero if any errors. Warnings (e.g. bloated theme leaves, thin leaves between 5 and 8 quotes) are surfaced but do not fail the run.

### `migrate.py` (historical)

Encodes the routing rules used to migrate the v1 flat `quotes.yaml` into the v2 theme/mood structure. Preserved for reproducibility and as documentation of the routing decisions taken on 2026-05-13. Not part of the day-to-day workflow.

## When to run validate.py

- After editing any leaf YAML.
- After adding new entries (especially from bulk imports).
- After moving entries between leaves.
- After running any bulk text replacement (e.g. character substitutions in source attributions).

Not wired into a git hook by design; run manually when you touch the bank.

## Bank structure recap

```
skills/quotespeak/
  SKILL.md
  references/
    themes.md             # taxonomy and theme x mood matrix
    examples.md           # corruption examples (substitutive vs additive)
    quotes/
      _universal/<mood>.yaml      # 10 always-loaded cross-cutters
      <theme>/_vibe.md            # theme overview, mood map, transitions
      <theme>/<mood>.yaml         # theme-specific quotes
```

11 themes (investigation, building, refactor, shipping, incident, planning, delegation, mentorship, waiting, archaeology, deprecation) by 10 moods (curious, deadpan, triumphant, ominous, exasperated, hopeful, philosophical, wistful, defiant, unhinged), with 62 valid theme/mood combinations per the matrix in `references/themes.md`.
