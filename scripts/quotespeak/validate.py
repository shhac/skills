#!/usr/bin/env python3
"""Validate skills/quotespeak/references/quotes.yaml.

Checks:
  - YAML parses
  - Every entry has the required fields (quote, source, topics, register)
  - `topics` is a list of strings
  - `register` is one of the canonical registers
  - No register token appears inside a `topics` list (cross-axis pollution)
  - No exact-duplicate quote text across entries

Exit codes:
  0  clean
  1  validation issues found
  2  cannot run (missing file, missing dependency, parse failure)
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "Missing dependency: pyyaml.\n"
        "See scripts/quotespeak/README.md for setup options.\n"
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
QUOTES_PATH = REPO_ROOT / "skills" / "quotespeak" / "references" / "quotes.yaml"

CANONICAL_REGISTERS = {
    "ominous", "triumphant", "exasperated", "deadpan", "hopeful",
    "defiant", "unhinged", "philosophical", "wistful", "snark",
    "reassuring", "foreboding", "smug",
}

REQUIRED_FIELDS = ("quote", "source", "topics", "register")


def main() -> int:
    if not QUOTES_PATH.exists():
        sys.stderr.write(f"ERROR: {QUOTES_PATH} not found\n")
        return 2

    try:
        with QUOTES_PATH.open() as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        sys.stderr.write(f"ERROR: YAML parse failure: {e}\n")
        return 2

    quotes = data.get("quotes") if isinstance(data, dict) else None
    if not isinstance(quotes, list):
        sys.stderr.write("ERROR: top-level 'quotes' key must be a list\n")
        return 2

    issues: list[str] = []

    for i, entry in enumerate(quotes, 1):
        label = f"entry {i}"
        if not isinstance(entry, dict):
            issues.append(f"{label}: not a mapping")
            continue
        label = f"entry {i} ({entry.get('quote', '<no quote>')!r})"

        for field in REQUIRED_FIELDS:
            value = entry.get(field)
            if value is None or value == "":
                issues.append(f"{label}: missing required field `{field}`")

        topics = entry.get("topics")
        if topics is not None and not (
            isinstance(topics, list) and all(isinstance(t, str) for t in topics)
        ):
            issues.append(f"{label}: `topics` must be a list of strings")

        register = entry.get("register")
        if register and register not in CANONICAL_REGISTERS:
            issues.append(
                f"{label}: unknown register {register!r} "
                f"(canonical: {sorted(CANONICAL_REGISTERS)})"
            )

        if isinstance(topics, list):
            overlap = sorted(set(topics) & CANONICAL_REGISTERS)
            if overlap:
                issues.append(
                    f"{label}: register tokens used as topics: {overlap} "
                    "— registers and topics are separate axes"
                )

    seen: dict[str, list[int]] = {}
    for i, entry in enumerate(quotes, 1):
        if isinstance(entry, dict):
            q = entry.get("quote")
            if isinstance(q, str):
                seen.setdefault(q, []).append(i)
    for q, ids in seen.items():
        if len(ids) > 1:
            issues.append(f"duplicate quote at entries {ids}: {q!r}")

    print(f"quotespeak: scanned {len(quotes)} entries in {QUOTES_PATH.relative_to(REPO_ROOT)}")
    if issues:
        print(f"FAIL: {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("OK: schema clean, registers canonical, no dups, no register/topic crossover")
    return 0


if __name__ == "__main__":
    sys.exit(main())
