#!/usr/bin/env python3
"""quotespeak v2 bank validator.

Checks:
1. Every theme directory has a _vibe.md.
2. Each _vibe.md's "Available moods" list matches the .yaml files in its directory.
3. Every leaf YAML has a `vibe:` field (warns if still TODO).
4. Every leaf YAML has >= 5 quotes (error) / >= 8 quotes (warn target).
5. Universal `_universal/*.yaml` count <= 30 each (warn).
6. No quote appears in both _universal/ and a theme leaf.
7. Required themes/moods present per the v2 taxonomy.

Usage:
    python3 validate.py [--root <path-to-quotes-dir>]

Default --root is the v2 staging area: .ai-cache/quotespeak-v2/references/quotes/
After cutover, point at skills/quotespeak/references/quotes/.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


THEMES = [
    "investigation",
    "building",
    "refactor",
    "shipping",
    "incident",
    "planning",
    "delegation",
    "mentorship",
    "waiting",
    "archaeology",
    "deprecation",
]

VALID_MOODS = {
    "curious",
    "deadpan",
    "triumphant",
    "ominous",
    "exasperated",
    "hopeful",
    "philosophical",
    "wistful",
    "defiant",
    "unhinged",
}

# The 62 valid theme×mood combinations per references/themes.md.
MATRIX = {
    "investigation": {"curious", "deadpan", "triumphant", "ominous", "exasperated", "philosophical", "defiant"},
    "building": {"deadpan", "triumphant", "exasperated", "hopeful", "philosophical"},
    "refactor": {"deadpan", "triumphant", "exasperated", "philosophical", "wistful", "defiant"},
    "shipping": {"deadpan", "triumphant", "ominous", "hopeful", "defiant"},
    "incident": {"deadpan", "ominous", "exasperated", "philosophical", "defiant", "unhinged"},
    "planning": {"deadpan", "ominous", "exasperated", "hopeful", "philosophical", "defiant"},
    "delegation": {"deadpan", "triumphant", "exasperated", "hopeful", "philosophical", "defiant"},
    "mentorship": {"deadpan", "hopeful", "philosophical", "wistful", "defiant"},
    "waiting": {"deadpan", "ominous", "exasperated", "hopeful", "philosophical", "wistful"},
    "archaeology": {"deadpan", "ominous", "exasperated", "philosophical", "wistful"},
    "deprecation": {"deadpan", "philosophical", "wistful", "defiant", "unhinged"},
}

UNIVERSAL_CAP = 30
UNIVERSAL_CAP_OVERRIDE = {"deadpan": 200}  # deadpan is the genuine catchall register
MIN_LEAF_QUOTES = 5
TARGET_LEAF_QUOTES = 8
MAX_THEME_LEAF_QUOTES = 20


def parse_vibe_md_moods(vibe_md_path: Path) -> list[str] | None:
    """Extract moods listed in the 'Available moods' section of a _vibe.md."""
    if not vibe_md_path.exists():
        return None
    text = vibe_md_path.read_text()
    match = re.search(r"## Available moods\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return None
    section = match.group(1)
    moods = re.findall(r"`(\w+)\.yaml`", section)
    seen: list[str] = []
    for m in moods:
        if m not in seen and m in VALID_MOODS:
            seen.append(m)
    return seen


def count_sentences(text: str) -> int:
    """Rough sentence-count heuristic for vibe blurbs."""
    return len(re.findall(r"[.!?]\s", text.strip() + " "))


def load_yaml(path: Path) -> dict | None:
    try:
        return yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        print(f"ERR:  {path}: invalid YAML - {e}", file=sys.stderr)
        return None


def check_leaf(path: Path, *, is_universal: bool, errors: list[str], warnings: list[str]) -> set[str]:
    """Validate a leaf YAML; return the set of quote strings it contains."""
    data = load_yaml(path)
    if data is None:
        return set()
    if not isinstance(data, dict):
        errors.append(f"{path}: root must be a mapping")
        return set()

    vibe = data.get("vibe", "")
    if not isinstance(vibe, str) or not vibe.strip():
        errors.append(f"{path}: missing or empty `vibe:` field")
    elif vibe.strip().lower().startswith("todo"):
        warnings.append(f"{path}: vibe is TODO - fill in Phase 4")
    elif count_sentences(vibe) < 6:
        warnings.append(f"{path}: vibe has <6 sentences (target 6-10 with concrete diction)")

    quotes = data.get("quotes") or []
    if not isinstance(quotes, list):
        errors.append(f"{path}: `quotes:` must be a list")
        return set()

    n = len(quotes)
    if n < MIN_LEAF_QUOTES:
        errors.append(f"{path}: only {n} quote(s); minimum {MIN_LEAF_QUOTES}")
    elif n < TARGET_LEAF_QUOTES:
        warnings.append(f"{path}: only {n} quote(s); target {TARGET_LEAF_QUOTES}")

    if is_universal:
        cap = UNIVERSAL_CAP_OVERRIDE.get(path.stem, UNIVERSAL_CAP)
        if n > cap:
            warnings.append(f"{path}: {n} quotes exceeds _universal cap of {cap}")
    if not is_universal and n > MAX_THEME_LEAF_QUOTES:
        warnings.append(f"{path}: {n} quotes - theme leaf bloated (cap {MAX_THEME_LEAF_QUOTES})")

    seen: set[str] = set()
    for i, q in enumerate(quotes):
        if not isinstance(q, dict):
            errors.append(f"{path}: quotes[{i}] is not a mapping")
            continue
        text = q.get("quote")
        if not text:
            errors.append(f"{path}: quotes[{i}] has no `quote:` text")
            continue
        if text in seen:
            errors.append(f"{path}: duplicate quote within file: {text[:60]!r}")
        seen.add(text)
        if not q.get("source"):
            warnings.append(f"{path}: quotes[{i}] ({text[:40]!r}) has no `source:`")

    return seen


def check_theme(theme_dir: Path, errors: list[str], warnings: list[str]) -> dict[str, set[str]]:
    """Validate a theme directory; return {mood: set-of-quote-strings}."""
    theme = theme_dir.name
    leaves: dict[str, set[str]] = {}

    vibe_md = theme_dir / "_vibe.md"
    if not vibe_md.exists():
        errors.append(f"{theme}: missing _vibe.md")
        return leaves

    listed_moods = parse_vibe_md_moods(vibe_md)
    if listed_moods is None or not listed_moods:
        errors.append(f"{theme}: _vibe.md has no parseable 'Available moods' section")
        listed_set = set()
    else:
        listed_set = set(listed_moods)

    actual_moods = {p.stem for p in theme_dir.glob("*.yaml")}

    missing_files = listed_set - actual_moods
    extra_files = actual_moods - listed_set
    for m in missing_files:
        warnings.append(f"{theme}: _vibe.md lists `{m}.yaml` but no file exists yet")
    for m in extra_files:
        errors.append(f"{theme}: file `{m}.yaml` exists but is not listed in _vibe.md")

    valid_moods_for_theme = MATRIX.get(theme, set())
    invalid = actual_moods - valid_moods_for_theme
    for m in invalid:
        errors.append(f"{theme}: `{m}.yaml` is not a valid mood for this theme (per matrix)")

    for yaml_path in sorted(theme_dir.glob("*.yaml")):
        mood = yaml_path.stem
        leaves[mood] = check_leaf(yaml_path, is_universal=False, errors=errors, warnings=warnings)

    return leaves


def check_universal(universal_dir: Path, errors: list[str], warnings: list[str]) -> dict[str, set[str]]:
    leaves: dict[str, set[str]] = {}
    if not universal_dir.exists():
        errors.append("_universal/ directory missing")
        return leaves
    for yaml_path in sorted(universal_dir.glob("*.yaml")):
        mood = yaml_path.stem
        if mood not in VALID_MOODS:
            errors.append(f"_universal/{mood}.yaml is not a valid mood name")
            continue
        leaves[mood] = check_leaf(yaml_path, is_universal=True, errors=errors, warnings=warnings)
    return leaves


def check_cross_dup(
    universal_leaves: dict[str, set[str]],
    theme_leaves: dict[str, dict[str, set[str]]],
    errors: list[str],
) -> None:
    """No quote should appear in both _universal/ and any theme leaf."""
    universal_all: set[str] = set()
    for s in universal_leaves.values():
        universal_all |= s
    for theme, moods in theme_leaves.items():
        for mood, quotes in moods.items():
            overlap = quotes & universal_all
            for q in overlap:
                errors.append(
                    f"{theme}/{mood}.yaml: quote also in _universal/ - pick one home: {q[:60]!r}"
                )


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    # Resolve for both staging (.ai-cache/quotespeak-v2/scripts/) and post-cutover (repo/scripts/quotespeak/) layouts.
    candidates = [
        script_dir.parent / "references" / "quotes",  # staging area pattern
        script_dir.parent.parent / "skills" / "quotespeak" / "references" / "quotes",  # post-cutover repo pattern
    ]
    default_root = next((c for c in candidates if c.is_dir()), candidates[0])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="path to the quotes/ root (default: staging area)",
    )
    args = parser.parse_args()

    root: Path = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    theme_leaves: dict[str, dict[str, set[str]]] = {}
    for theme in THEMES:
        theme_dir = root / theme
        if not theme_dir.is_dir():
            errors.append(f"theme directory missing: {theme}")
            continue
        theme_leaves[theme] = check_theme(theme_dir, errors, warnings)

    universal_leaves = check_universal(root / "_universal", errors, warnings)
    check_cross_dup(universal_leaves, theme_leaves, errors)

    # Surface counts
    print("Leaf counts:")
    for theme in THEMES:
        moods = theme_leaves.get(theme, {})
        if moods:
            line = ", ".join(f"{m}={len(q)}" for m, q in sorted(moods.items()))
            print(f"  {theme}: {line}")
    if universal_leaves:
        line = ", ".join(f"{m}={len(q)}" for m, q in sorted(universal_leaves.items()))
        print(f"  _universal: {line}")

    print()
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERR:  {e}", file=sys.stderr)

    print(f"\nTotals: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
