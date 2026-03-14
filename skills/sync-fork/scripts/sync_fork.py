"""sync-fork: Git fork synchronization utilities.

Deterministic helpers for classifying branches, analyzing divergence,
and building dependency graphs when syncing a fork with its upstream.

Invoked by Claude via: python3 scripts/sync_fork.py <subcommand> [options]

Requires Python 3.9+ (stdlib only, no external dependencies).
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Optional, List, Dict


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(*args: str, check: bool = True) -> str:
    """Run a git command and return stripped stdout."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, check=False,
    )
    if check and result.returncode != 0:
        print(f"error: git {' '.join(args)}", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def git_lines(*args: str) -> List[str]:
    """Run a git command and return non-empty stdout lines."""
    out = git(*args)
    return [line for line in out.splitlines() if line.strip()]


def git_test(*args: str) -> bool:
    """Run a git command and return True if exit code is 0."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def git_count(*args: str) -> int:
    """Run a git rev-list --count and return the integer."""
    out = git("rev-list", "--count", *args)
    return int(out)


# ---------------------------------------------------------------------------
# Branch listing
# ---------------------------------------------------------------------------

def remote_branches(remote: str) -> List[str]:
    """List branch names on a remote (stripped of remote/ prefix, excluding HEAD)."""
    lines = git_lines("branch", "-r", "--list", f"{remote}/*")
    branches = []
    for line in lines:
        line = line.strip()
        if " -> " in line:
            continue
        name = line.removeprefix(f"{remote}/")
        if name != "HEAD":
            branches.append(name)
    return branches


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PartialBranch:
    branch: str
    matched: int
    unmatched: int


@dataclass
class Classification:
    shared: List[str]
    fork_only_merged: List[str]
    fork_only_promoted: List[str]
    fork_only_active: List[str]
    fork_only_partial: List[PartialBranch]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fork_only_partial"] = [asdict(p) for p in self.fork_only_partial]
        return d


@dataclass
class BranchDivergence:
    branch: str
    upstream_only: int
    fork_only: int
    rewrite: bool
    fork_merges_only: bool  # True if all fork-only commits are merges (normal Phase 4 state)
    reverts: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DependencyGraph:
    parents: Dict[str, str]
    order: List[str]
    orphaned: List[str]
    targets: Dict[str, str]

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def classify_branches(fork: str, upstream: str) -> Classification:
    """Classify all branches into shared, merged, promoted, partial, active."""
    fork_set = set(remote_branches(fork))
    upstream_set = set(remote_branches(upstream))

    shared = sorted(fork_set & upstream_set)

    fork_only = sorted(fork_set - upstream_set)

    # Determine the default upstream branch for equivalence checks
    default_branch = _default_branch(shared)

    merged = []
    promoted = []
    partial = []
    active = []

    for branch in fork_only:
        # Check against each shared branch (not just default) for multi-target support
        is_merged = False
        is_promoted = False
        for target in shared:
            if git_test("merge-base", "--is-ancestor",
                         f"{fork}/{branch}", f"{upstream}/{target}"):
                is_merged = True
                break
        if is_merged:
            merged.append(branch)
            continue

        for target in shared:
            cherry_lines = git_lines(
                "log", "--oneline", "--cherry-pick", "--right-only",
                f"{upstream}/{target}...{fork}/{branch}",
            )
            if not cherry_lines:
                is_promoted = True
                break
        if is_promoted:
            promoted.append(branch)
            continue

        # Check for partial promotion via cherry-mark (against default branch)
        mark_lines = git_lines(
            "log", "--oneline", "--cherry-mark", "--right-only",
            f"{upstream}/{default_branch}...{fork}/{branch}",
        )
        matched_count = sum(1 for l in mark_lines if l.startswith("="))
        unmatched_count = sum(1 for l in mark_lines if l.startswith("+"))

        if matched_count > 0 and unmatched_count > 0:
            partial.append(PartialBranch(branch, matched_count, unmatched_count))
            active.append(branch)
        else:
            active.append(branch)

    return Classification(
        shared=shared,
        fork_only_merged=merged,
        fork_only_promoted=promoted,
        fork_only_active=active,
        fork_only_partial=partial,
    )


def compute_divergence(
    fork: str, upstream: str, shared: List[str]
) -> List[BranchDivergence]:
    """For each shared branch, compute divergence between fork and upstream."""
    results = []
    for branch in shared:
        upstream_only = git_count(f"{fork}/{branch}..{upstream}/{branch}")
        fork_only_count = git_count(f"{upstream}/{branch}..{fork}/{branch}")
        rewrite = upstream_only > 0 and fork_only_count > 0

        # Check if fork-only commits are all merges (normal Phase 4 state,
        # not a real history rewrite)
        fork_merges_only = False
        if rewrite and fork_only_count > 0:
            total = git_count(f"{upstream}/{branch}..{fork}/{branch}")
            merges = git_count(
                "--merges", f"{upstream}/{branch}..{fork}/{branch}")
            fork_merges_only = (total > 0 and total == merges)

        revert_lines = git_lines(
            "log", "--oneline", "--grep=^Revert",
            f"{fork}/{branch}..{upstream}/{branch}",
        )
        reverts = [line.strip() for line in revert_lines]

        results.append(BranchDivergence(
            branch=branch,
            upstream_only=upstream_only,
            fork_only=fork_only_count,
            rewrite=rewrite,
            fork_merges_only=fork_merges_only,
            reverts=reverts,
        ))
    return results


def build_graph(
    branches: List[str],
    shared: List[str],
    backup_prefix: str = "sync-fork/pre-reset",
    use_remote_refs: Optional[str] = None,
) -> DependencyGraph:
    """Build dependency graph with topological ordering.

    Args:
        branches: Fork-only active branches to graph.
        shared: Shared branch names.
        backup_prefix: Local ref prefix for shared branch backups.
        use_remote_refs: If set, use <remote>/<branch> instead of backup refs
                         for shared branches (for plan/dry-run mode before
                         backups exist).
    """
    parents: Dict[str, str] = {}
    orphaned: List[str] = []
    all_candidates = list(shared) + list(branches)

    for branch in branches:
        best_parent = None
        best_distance = float("inf")

        for candidate in all_candidates:
            if candidate == branch:
                continue

            # Resolve the ref to check ancestry against
            if candidate in shared:
                if use_remote_refs:
                    candidate_ref = f"{use_remote_refs}/{candidate}"
                else:
                    candidate_ref = f"{backup_prefix}/{candidate}"
            else:
                candidate_ref = candidate

            if not git_test("merge-base", "--is-ancestor", candidate_ref, branch):
                continue

            distance = git_count(f"{candidate_ref}..{branch}")
            if distance < best_distance:
                best_distance = distance
                best_parent = candidate

        if best_parent is None:
            orphaned.append(branch)
        else:
            parents[branch] = best_parent

    # Topological sort
    order = _topo_sort(parents, branches, shared)

    # Trace each branch to its root shared branch
    targets = _resolve_targets(parents, shared)

    return DependencyGraph(
        parents=parents,
        order=order,
        orphaned=orphaned,
        targets=targets,
    )


def generate_plan(fork: str, upstream: str) -> dict:
    """Combine classify + divergence + graph into a full dry-run plan."""
    cls = classify_branches(fork, upstream)
    divs = compute_divergence(fork, upstream, cls.shared)

    graph = None
    actions = {}

    if cls.fork_only_active:
        # In plan mode, backups don't exist yet — use fork remote refs
        graph = build_graph(
            branches=cls.fork_only_active,
            shared=cls.shared,
            use_remote_refs=fork,
        )

        # Build action list
        rebase_actions = []
        for branch in graph.order:
            parent = graph.parents.get(branch)
            if parent and parent in cls.shared:
                rebase_actions.append(f"{branch} onto {parent}")
            elif parent:
                rebase_actions.append(f"{branch} onto {parent} (--onto)")
            else:
                rebase_actions.append(f"{branch} (orphaned, needs user input)")

        merge_actions = []
        for branch in graph.order:
            target = graph.targets.get(branch)
            if target:
                merge_actions.append(f"{branch} into {target}")

        actions = {
            "delete_remote": cls.fork_only_merged + cls.fork_only_promoted,
            "reset": cls.shared,
            "backup": cls.shared + cls.fork_only_active,
            "rebase": rebase_actions,
            "merge": merge_actions,
        }

    return {
        "classification": cls.to_dict(),
        "divergence": [d.to_dict() for d in divs],
        "graph": graph.to_dict() if graph else None,
        "actions": actions,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_branch(shared: List[str]) -> str:
    """Pick the default branch from shared branches."""
    for name in ("main", "master"):
        if name in shared:
            return name
    return shared[0] if shared else "main"


def _topo_sort(
    parents: Dict[str, str],
    branches: List[str],
    shared: List[str],
) -> List[str]:
    """Topologically sort branches (parents before children)."""
    graph: Dict[str, set] = {}
    shared_set = set(shared)

    for branch in branches:
        parent = parents.get(branch)
        if parent and parent not in shared_set:
            # Depends on another fork-only branch
            graph[branch] = {parent}
        else:
            graph[branch] = set()

    # Ensure all fork-only parents are in the graph
    for branch in branches:
        if branch not in graph:
            graph[branch] = set()

    sorter = TopologicalSorter(graph)
    try:
        return list(sorter.static_order())
    except Exception as e:
        print(f"error: cycle in dependency graph: {e}", file=sys.stderr)
        sys.exit(1)


def _resolve_targets(
    parents: Dict[str, str], shared: List[str]
) -> Dict[str, str]:
    """Trace each branch to its root shared branch."""
    shared_set = set(shared)
    targets: Dict[str, str] = {}

    for branch in parents:
        current = branch
        visited = set()
        while current in parents and current not in shared_set:
            if current in visited:
                break
            visited.add(current)
            current = parents[current]
        if current in shared_set:
            targets[branch] = current

    return targets


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_compact_classification(cls: Classification) -> str:
    lines = []
    lines.append(f"shared: {','.join(cls.shared) or '(none)'}")
    lines.append(f"fork-only-merged: {','.join(cls.fork_only_merged) or '(none)'}")
    lines.append(f"fork-only-promoted: {','.join(cls.fork_only_promoted) or '(none)'}")
    lines.append(f"fork-only-active: {','.join(cls.fork_only_active) or '(none)'}")
    if cls.fork_only_partial:
        parts = [
            f"{p.branch}(matched={p.matched},unmatched={p.unmatched})"
            for p in cls.fork_only_partial
        ]
        lines.append(f"fork-only-partial: {','.join(parts)}")
    return "\n".join(lines)


def format_compact_divergence(divs: List[BranchDivergence]) -> str:
    lines = []
    for d in divs:
        reverts_count = len(d.reverts)
        lines.append(
            f"{d.branch}: upstream_only={d.upstream_only},"
            f"fork_only={d.fork_only},"
            f"rewrite={str(d.rewrite).lower()},"
            f"fork_merges_only={str(d.fork_merges_only).lower()},"
            f"reverts={reverts_count}"
        )
    return "\n".join(lines)


def format_compact_graph(graph: DependencyGraph) -> str:
    lines = []
    if graph.parents:
        pairs = [f"{b}={p}" for b, p in graph.parents.items()]
        lines.append(f"parent: {','.join(pairs)}")
    else:
        lines.append("parent: (none)")
    lines.append(f"order: {','.join(graph.order) or '(none)'}")
    lines.append(f"orphaned: {','.join(graph.orphaned) or '(none)'}")
    if graph.targets:
        pairs = [f"{b}={t}" for b, t in graph.targets.items()]
        lines.append(f"target: {','.join(pairs)}")
    else:
        lines.append("target: (none)")
    return "\n".join(lines)


def format_compact_plan(plan: dict) -> str:
    sections = []

    sections.append("=== classification ===")
    cls = Classification(**{
        k: [PartialBranch(**p) for p in v] if k == "fork_only_partial" else v
        for k, v in plan["classification"].items()
    })
    sections.append(format_compact_classification(cls))

    sections.append("\n=== divergence ===")
    divs = [BranchDivergence(**d) for d in plan["divergence"]]
    sections.append(format_compact_divergence(divs))

    if plan.get("graph"):
        sections.append("\n=== dependency graph ===")
        graph = DependencyGraph(**plan["graph"])
        sections.append(format_compact_graph(graph))

    if plan.get("actions"):
        sections.append("\n=== actions ===")
        a = plan["actions"]
        sections.append(f"delete-remote: {','.join(a.get('delete_remote', [])) or '(none)'}")
        sections.append(f"reset: {','.join(a.get('reset', [])) or '(none)'}")
        sections.append(f"backup: {','.join(a.get('backup', [])) or '(none)'}")
        sections.append(f"rebase: {','.join(a.get('rebase', [])) or '(none)'}")
        sections.append(f"merge: {','.join(a.get('merge', [])) or '(none)'}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state(path: Path) -> Optional[dict]:
    """Load sync state from file, or None if it doesn't exist."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"warning: could not read state file: {e}", file=sys.stderr)
        return None


def save_state(state: dict, path: Path) -> None:
    """Write sync state to file."""
    path.write_text(json.dumps(state, indent=2) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_classify(args: argparse.Namespace) -> None:
    cls = classify_branches(args.fork, args.upstream)
    if args.json:
        print(json.dumps(cls.to_dict(), indent=2))
    else:
        print(format_compact_classification(cls))


def cmd_divergence(args: argparse.Namespace) -> None:
    cls = classify_branches(args.fork, args.upstream)
    divs = compute_divergence(args.fork, args.upstream, cls.shared)
    if args.json:
        print(json.dumps([d.to_dict() for d in divs], indent=2))
    else:
        print(format_compact_divergence(divs))


def cmd_graph(args: argparse.Namespace) -> None:
    branches = [b for b in args.branches.split(",") if b]
    shared = [b for b in args.shared.split(",") if b]
    graph = build_graph(
        branches=branches,
        shared=shared,
        backup_prefix=args.backup_prefix,
        use_remote_refs=args.use_remote_refs,
    )
    if args.json:
        print(json.dumps(graph.to_dict(), indent=2))
    else:
        print(format_compact_graph(graph))


def cmd_plan(args: argparse.Namespace) -> None:
    plan = generate_plan(args.fork, args.upstream)
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(format_compact_plan(plan))


def cmd_state(args: argparse.Namespace) -> None:
    git_dir = git("rev-parse", "--git-dir")
    state_path = Path(git_dir) / "sync-fork-state.json"

    if args.state_action == "read":
        state = load_state(state_path)
        if state is None:
            print("no state file found")
            sys.exit(1)
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            for key, value in state.items():
                if isinstance(value, (dict, list)):
                    print(f"{key}: {json.dumps(value)}")
                else:
                    print(f"{key}: {value}")

    elif args.state_action == "write":
        if not args.data:
            print("error: --data required for state write", file=sys.stderr)
            sys.exit(1)
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        save_state(data, state_path)
        print(f"state written to {state_path}")

    elif args.state_action == "delete":
        if state_path.exists():
            state_path.unlink()
            print("state file deleted")
        else:
            print("no state file to delete")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sync_fork",
        description="Git fork synchronization utilities for Claude.",
    )
    parser.add_argument("--fork", help="Fork remote name")
    parser.add_argument("--upstream", help="Upstream remote name")
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of compact key-value format",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "classify",
        help="Classify branches as shared, merged, promoted, or active",
    )

    subparsers.add_parser(
        "divergence",
        help="Show divergence between fork and upstream for shared branches",
    )

    graph_parser = subparsers.add_parser(
        "graph",
        help="Build dependency graph and topological order for fork-only branches",
    )
    graph_parser.add_argument(
        "--branches", required=True,
        help="Comma-separated list of fork-only active branches",
    )
    graph_parser.add_argument(
        "--shared", required=True,
        help="Comma-separated list of shared branches",
    )
    graph_parser.add_argument(
        "--backup-prefix", default="sync-fork/pre-reset",
        help="Ref prefix for shared branch backups (default: sync-fork/pre-reset)",
    )
    graph_parser.add_argument(
        "--use-remote-refs",
        help="Use <remote>/<branch> instead of backup refs (for dry-run before backups exist)",
    )

    subparsers.add_parser(
        "plan",
        help="Full dry-run: classify + divergence + graph + proposed actions",
    )

    state_parser = subparsers.add_parser(
        "state",
        help="Read, write, or delete sync state file in .git/",
    )
    state_parser.add_argument(
        "state_action", choices=["read", "write", "delete"],
        help="State operation to perform",
    )
    state_parser.add_argument(
        "--data", help="JSON string to write (required for 'write')",
    )

    args = parser.parse_args()

    # Validate remote args for commands that need them
    if args.command in ("classify", "divergence", "plan"):
        if not args.fork or not args.upstream:
            parser.error(f"--fork and --upstream are required for '{args.command}'")

    dispatch = {
        "classify": cmd_classify,
        "divergence": cmd_divergence,
        "graph": cmd_graph,
        "plan": cmd_plan,
        "state": cmd_state,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
