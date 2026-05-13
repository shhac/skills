# quotespeak scripts

Helper scripts for maintaining `skills/quotespeak/references/quotes.yaml`.

## Requirements

Both scripts depend on [PyYAML](https://pyyaml.org/). Pick whichever setup you prefer:

**Option A — `uv` (no setup, recommended):**

```bash
uv run --with pyyaml scripts/quotespeak/validate.py
uv run --with pyyaml scripts/quotespeak/clean.py
```

**Option B — virtualenv:**

```bash
python3 -m venv .venv
.venv/bin/pip install pyyaml
.venv/bin/python scripts/quotespeak/validate.py
.venv/bin/python scripts/quotespeak/clean.py
```

**Option C — system pip (macOS users may need `--break-system-packages`):**

```bash
pip install --user pyyaml
python3 scripts/quotespeak/validate.py
```

If PyYAML isn't installed, each script exits with code `2` and a pointer back to this file.

## Scripts

### `validate.py` (read-only)

Exits non-zero if `quotes.yaml` has any of:

- A missing required field on any entry (`quote`, `source`, `topics`, `register`).
- A `topics` value that isn't a list of strings.
- A `register` value outside the canonical set of 13.
- A register token that has leaked into a `topics:` list (registers and topics are separate axes — `foreboding` is a register, not a situational tag).
- Two entries that share the exact same `quote` text.

Reports every issue it finds, not just the first.

### `clean.py` (writes in place)

Applies two safe, idempotent fixes:

1. **Removes duplicate quote entries** — keeps the first occurrence, drops the rest.
2. **Strips register tokens from `topics:` lists** — removes the offending tag and leaves the rest intact.

Edits happen line-by-line so YAML comments, section dividers, and entry ordering are preserved. The result is re-parsed after writing; if parsing fails the original file is restored.

Running `clean.py` twice in a row is a no-op.

## When to run

- **Before committing** any change to `quotes.yaml` — `clean.py` first to apply the safe fixes, then `validate.py` to confirm nothing else is wrong.
- **After bulk imports** — large batches of new entries are the most common source of accidental duplicates.
- **After a refactor of the topic taxonomy** — `validate.py` catches register/topic crossover that's easy to introduce when renaming tags.

Neither script is wired into a git hook by design; run them when you touch the bank.
