#!/usr/bin/env python3
"""Apply safe, idempotent fixes to skills/quotespeak/references/quotes.yaml.

Fixes applied:
  1. Remove exact-duplicate quote entries (keeps the first occurrence).
  2. Strip register tokens that leaked into `topics:` lists.

The script edits the file line-by-line so YAML comments, section dividers,
and entry ordering are preserved. The result is re-parsed after writing; if
parsing fails the original content is restored and the script exits non-zero.

Exit codes:
  0  cleaned successfully (or already clean)
  1  parse failure or post-write verification failure
  2  cannot run (missing file, missing dependency)
"""

from __future__ import annotations

import re
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

QUOTE_LINE_RE = re.compile(r'^  - quote: "(.+)"\s*$')
TOPICS_LINE_RE = re.compile(r'^(    topics: \[)(.+)(\]\s*)$')


def find_entry_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return [(quote_text, start_line_idx, end_line_idx_inclusive)] for each entry.

    An entry's block is the `- quote: ...` line plus the indented field lines that
    follow, stopping at the next entry start, a section comment line, or EOF.
    Trailing blank lines belonging to the block separator are NOT included.
    """
    blocks: list[tuple[str, int, int]] = []
    current_start: int | None = None
    current_quote: str | None = None

    def close(end_exclusive: int) -> None:
        nonlocal current_start, current_quote
        if current_start is None or current_quote is None:
            return
        end = end_exclusive - 1
        while end > current_start and lines[end].strip() == "":
            end -= 1
        blocks.append((current_quote, current_start, end))
        current_start = None
        current_quote = None

    for i, line in enumerate(lines):
        m = QUOTE_LINE_RE.match(line)
        if m:
            close(i)
            current_start = i
            current_quote = m.group(1)
            continue
        if current_start is not None and line.lstrip().startswith("#"):
            close(i)

    close(len(lines))
    return blocks


def remove_duplicate_entries(lines: list[str]) -> tuple[list[str], int]:
    blocks = find_entry_blocks(lines)
    seen: set[str] = set()
    to_remove: list[tuple[int, int]] = []
    for quote, start, end in blocks:
        if quote in seen:
            to_remove.append((start, end))
        else:
            seen.add(quote)

    if not to_remove:
        return lines, 0

    new_lines = list(lines)
    for start, end in sorted(to_remove, reverse=True):
        del new_lines[start:end + 1]
        if start < len(new_lines) and new_lines[start].strip() == "":
            del new_lines[start]
    return new_lines, len(to_remove)


def strip_registers_from_topics(lines: list[str]) -> tuple[list[str], int]:
    fixed = 0
    new_lines: list[str] = []
    for line in lines:
        m = TOPICS_LINE_RE.match(line)
        if not m:
            new_lines.append(line)
            continue
        prefix, inner, suffix = m.groups()
        tags = [t.strip() for t in inner.split(",") if t.strip()]
        cleaned = [t for t in tags if t not in CANONICAL_REGISTERS]
        if cleaned != tags and cleaned:
            new_lines.append(f"{prefix}{', '.join(cleaned)}{suffix.rstrip()}")
            fixed += 1
        else:
            new_lines.append(line)
    return new_lines, fixed


def main() -> int:
    if not QUOTES_PATH.exists():
        sys.stderr.write(f"ERROR: {QUOTES_PATH} not found\n")
        return 2

    original_text = QUOTES_PATH.read_text()
    lines = original_text.splitlines()

    blocks = find_entry_blocks(lines)
    print(f"quotespeak: scanned {len(blocks)} entries in {QUOTES_PATH.relative_to(REPO_ROOT)}")

    lines, dup_removed = remove_duplicate_entries(lines)
    if dup_removed:
        print(f"  removed {dup_removed} duplicate quote {'entry' if dup_removed == 1 else 'entries'}")

    lines, topic_fixes = strip_registers_from_topics(lines)
    if topic_fixes:
        print(f"  cleaned register tokens from {topic_fixes} topics line(s)")

    if not dup_removed and not topic_fixes:
        print("already tidy — no changes")
        return 0

    new_text = "\n".join(lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    QUOTES_PATH.write_text(new_text)

    try:
        with QUOTES_PATH.open() as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        QUOTES_PATH.write_text(original_text)
        sys.stderr.write(
            f"ERROR: post-write parse failed ({e}); reverted to original.\n"
        )
        return 1

    print("done — run validate.py to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
