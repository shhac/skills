"""restack: Stacked branch management utilities.

Infers dependency graphs from git history and cascades rebases through
stacked branches. No persistent metadata — the graph is derived fresh
from merge-base ancestry and commit distance each time.

Invoked by Claude via: python3 scripts/restack.py <subcommand> [options]

Requires Python 3.9+ (stdlib only, no external dependencies).
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from graphlib import TopologicalSorter, CycleError
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(*args: str, check: bool = True) -> str:
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
    out = git(*args)
    return [line for line in out.splitlines() if line.strip()]


def git_test(*args: str) -> bool:
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def git_count(*args: str) -> int:
    out = git("rev-list", "--count", *args)
    return int(out)


def git_rev(ref: str) -> str:
    return git("rev-parse", ref)


def git_merge_base(a: str, b: str) -> Optional[str]:
    result = subprocess.run(
        ["git", "merge-base", a, b],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Branch discovery
# ---------------------------------------------------------------------------

def detect_trunk() -> str:
    """Detect the trunk branch (main or master)."""
    for name in ("main", "master"):
        if git_test("rev-parse", "--verify", name):
            return name
    print("error: could not detect trunk branch (no main or master)", file=sys.stderr)
    sys.exit(1)


def discover_branches(
    trunk: str,
    explicit: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> List[str]:
    """Find branches to analyze.

    Priority: explicit list > prefix match > all local branches ahead of trunk.
    """
    if explicit:
        for b in explicit:
            if not git_test("rev-parse", "--verify", b):
                print(f"error: branch '{b}' does not exist", file=sys.stderr)
                sys.exit(1)
        return explicit

    local = git_lines("for-each-ref", "--format=%(refname:short)", "refs/heads/")
    candidates = [b for b in local if b != trunk]

    if prefix:
        candidates = [b for b in candidates if b.startswith(prefix)]

    # Filter to branches ahead of trunk (have commits not in trunk)
    ahead = []
    for b in candidates:
        # Skip backup refs
        if b.startswith("restack/") or b.startswith("sync-fork/"):
            continue
        count = git_count(f"{trunk}..{b}")
        if count > 0:
            ahead.append(b)

    return sorted(ahead)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Ambiguity:
    branches: List[str]
    fork_point: str
    details: List[Dict[str, str]]  # [{branch, commits, first_commit_ts}]


@dataclass
class GraphResult:
    parents: Dict[str, str]
    order: List[str]
    orphaned: List[str]
    targets: Dict[str, str]       # branch -> root trunk
    ambiguities: List[Ambiguity]


@dataclass
class BranchStatus:
    branch: str
    parent: str
    commits: int
    state: str  # ok, needs-restack, landed


@dataclass
class StatusResult:
    trunk: str
    trunk_behind: int
    branches: List[BranchStatus]
    graph: GraphResult


# ---------------------------------------------------------------------------
# Graph inference
# ---------------------------------------------------------------------------

def build_graph(trunk: str, branches: List[str]) -> GraphResult:
    """Infer dependency graph from git history."""
    parents: Dict[str, str] = {}
    orphaned: List[str] = []
    all_candidates = [trunk] + list(branches)

    for branch in branches:
        best_parent = None
        best_distance = float("inf")

        for candidate in all_candidates:
            if candidate == branch:
                continue

            if not git_test("merge-base", "--is-ancestor", candidate, branch):
                continue

            distance = git_count(f"{candidate}..{branch}")
            if distance < best_distance:
                best_distance = distance
                best_parent = candidate

        if best_parent is None:
            orphaned.append(branch)
        else:
            parents[branch] = best_parent

    order = _topo_sort(parents, branches, trunk)
    targets = _resolve_targets(parents, trunk)
    ambiguities = _detect_ambiguities(parents, branches, trunk)

    return GraphResult(
        parents=parents,
        order=order,
        orphaned=orphaned,
        targets=targets,
        ambiguities=ambiguities,
    )


def _detect_ambiguities(
    parents: Dict[str, str],
    branches: List[str],
    trunk: str,
) -> List[Ambiguity]:
    """Detect branches that fork from the same commit on the same parent."""
    # Group siblings by (parent, fork_point)
    groups: Dict[Tuple[str, str], List[str]] = {}
    for branch in branches:
        parent = parents.get(branch)
        if parent is None:
            continue
        mb = git_merge_base(parent, branch)
        if mb is None:
            continue
        key = (parent, mb)
        groups.setdefault(key, []).append(branch)

    ambiguities = []
    for (parent, fork_point), siblings in groups.items():
        if len(siblings) < 2:
            continue

        # Check if any sibling is an ancestor of another — if so, not ambiguous
        truly_ambiguous = []
        for i, a in enumerate(siblings):
            is_ancestor_of_any = False
            for j, b in enumerate(siblings):
                if i != j and git_test("merge-base", "--is-ancestor", a, b):
                    is_ancestor_of_any = True
                    break
            if not is_ancestor_of_any:
                # Check if any sibling is ancestor of this one
                has_ancestor_sibling = False
                for j, b in enumerate(siblings):
                    if i != j and git_test("merge-base", "--is-ancestor", b, a):
                        has_ancestor_sibling = True
                        break
                if not has_ancestor_sibling:
                    truly_ambiguous.append(a)

        if len(truly_ambiguous) < 2:
            continue

        details = []
        for b in truly_ambiguous:
            commits = git_count(f"{fork_point}..{b}")
            ts = git("log", "--format=%aI", "--reverse", f"{fork_point}..{b}",
                     "--", check=False).splitlines()
            first_ts = ts[0].strip() if ts else "unknown"
            details.append({
                "branch": b,
                "commits": str(commits),
                "first_commit_ts": first_ts,
            })

        ambiguities.append(Ambiguity(
            branches=truly_ambiguous,
            fork_point=fork_point[:8],
            details=details,
        ))

    return ambiguities


def _topo_sort(
    parents: Dict[str, str],
    branches: List[str],
    trunk: str,
) -> List[str]:
    """Topologically sort branches (parents before children)."""
    graph: Dict[str, set] = {}
    for branch in branches:
        parent = parents.get(branch)
        if parent and parent != trunk and parent in parents:
            graph[branch] = {parent}
        else:
            graph[branch] = set()
    for branch in branches:
        graph.setdefault(branch, set())

    sorter = TopologicalSorter(graph)
    try:
        return list(sorter.static_order())
    except CycleError as e:
        print(f"error: cycle in dependency graph: {e}", file=sys.stderr)
        sys.exit(1)


def _resolve_targets(parents: Dict[str, str], trunk: str) -> Dict[str, str]:
    """Trace each branch to its root (trunk)."""
    targets: Dict[str, str] = {}
    for branch in parents:
        current = branch
        visited = set()
        while current in parents and current != trunk:
            if current in visited:
                break
            visited.add(current)
            current = parents[current]
        targets[branch] = trunk
    return targets


# ---------------------------------------------------------------------------
# Status computation
# ---------------------------------------------------------------------------

def compute_status(trunk: str, branches: List[str]) -> StatusResult:
    """Compute full status: graph + per-branch state."""
    # Trunk behind remote
    trunk_behind = 0
    remote_ref = f"origin/{trunk}"
    if git_test("rev-parse", "--verify", remote_ref):
        trunk_behind = git_count(f"{trunk}..{remote_ref}")

    graph = build_graph(trunk, branches)

    statuses = []
    for branch in graph.order:
        parent = graph.parents.get(branch, trunk)
        commits = git_count(f"{parent}..{branch}")
        state = _branch_state(branch, parent, trunk)
        statuses.append(BranchStatus(
            branch=branch,
            parent=parent,
            commits=commits,
            state=state,
        ))

    # Add orphaned branches
    for branch in graph.orphaned:
        commits = git_count(f"{trunk}..{branch}")
        statuses.append(BranchStatus(
            branch=branch,
            parent="(orphaned)",
            commits=commits,
            state="orphaned",
        ))

    return StatusResult(
        trunk=trunk,
        trunk_behind=trunk_behind,
        branches=statuses,
        graph=graph,
    )


def _branch_state(branch: str, parent: str, trunk: str) -> str:
    """Determine branch state relative to its parent."""
    # Check if landed (all patches in trunk)
    cherry = git_lines(
        "log", "--oneline", "--cherry-pick", "--right-only",
        f"{trunk}...{branch}",
    )
    if not cherry:
        return "landed"

    # Check if parent's tip == merge-base (branch is up to date with parent)
    parent_tip = git_rev(parent)
    mb = git_merge_base(parent, branch)
    if mb == parent_tip:
        return "ok"

    return "needs-restack"


# ---------------------------------------------------------------------------
# Landed branch detection
# ---------------------------------------------------------------------------

def detect_landed(trunk: str, branches: List[str]) -> List[str]:
    """Find branches whose patches are all in trunk."""
    landed = []
    for branch in branches:
        # Check exact merge (tip is ancestor of trunk)
        if git_test("merge-base", "--is-ancestor", branch, trunk):
            landed.append(branch)
            continue
        # Check patch equivalence
        cherry = git_lines(
            "log", "--oneline", "--cherry-pick", "--right-only",
            f"{trunk}...{branch}",
        )
        if not cherry:
            landed.append(branch)
    return landed


# ---------------------------------------------------------------------------
# Backup ref management
# ---------------------------------------------------------------------------

BACKUP_PREFIX = "restack/pre-rebase"


def create_backups(branches: List[str]) -> Dict[str, str]:
    """Create backup refs for all branches. Returns {branch: backup_ref}."""
    backups = {}
    for branch in branches:
        ref = f"{BACKUP_PREFIX}/{branch}"
        git("branch", "-f", ref, branch)
        backups[branch] = ref
    return backups


def find_existing_backups() -> List[str]:
    """Find existing restack backup branches."""
    return git_lines("for-each-ref", "--format=%(refname:short)",
                     f"refs/heads/{BACKUP_PREFIX}/")


def delete_backups() -> List[str]:
    """Delete all restack backup refs. Returns deleted ref names."""
    backups = find_existing_backups()
    if backups:
        git("branch", "-D", *backups)
    return backups


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_compact_status(status: StatusResult) -> str:
    lines = []
    behind_str = f" ({status.trunk_behind} behind origin)" if status.trunk_behind > 0 else ""
    lines.append(f"trunk: {status.trunk}{behind_str}")

    # Build tree structure
    children: Dict[str, List[BranchStatus]] = {}
    for bs in status.branches:
        children.setdefault(bs.parent, []).append(bs)

    def render_tree(parent: str, indent: str = "") -> None:
        for i, bs in enumerate(children.get(parent, [])):
            is_last = i == len(children.get(parent, [])) - 1
            connector = "└─" if is_last else "├─"
            state_str = bs.state
            lines.append(f"{indent}{connector} {bs.branch} ({bs.commits} commits, {state_str})")
            next_indent = indent + ("   " if is_last else "│  ")
            render_tree(bs.branch, next_indent)

    lines.append("")
    render_tree(status.trunk)

    # Render orphaned
    orphaned = [bs for bs in status.branches if bs.state == "orphaned"]
    if orphaned:
        lines.append("")
        for bs in orphaned:
            lines.append(f"orphaned: {bs.branch} ({bs.commits} commits)")

    # Render ambiguities
    if status.graph.ambiguities:
        lines.append("")
        for amb in status.graph.ambiguities:
            branch_strs = []
            for d in amb.details:
                branch_strs.append(f"{d['branch']}({d['commits']} commits, first={d['first_commit_ts'][:10]})")
            lines.append(f"ambiguous: {','.join(branch_strs)} fork from {amb.fork_point}")

    return "\n".join(lines)


def format_compact_graph(graph: GraphResult) -> str:
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

    if graph.ambiguities:
        for amb in graph.ambiguities:
            branch_strs = []
            for d in amb.details:
                branch_strs.append(
                    f"{d['branch']}({d['commits']} commits, first={d['first_commit_ts'][:10]})"
                )
            lines.append(f"ambiguous: {','.join(branch_strs)} fork from {amb.fork_point}")

    return "\n".join(lines)


def _to_dict(obj) -> dict:
    """Recursively convert dataclasses to dicts."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _to_dict(v) for k, v in asdict(obj).items()}
    return obj


# ---------------------------------------------------------------------------
# State management (ephemeral, for interrupted operations)
# ---------------------------------------------------------------------------

def state_path() -> Path:
    git_dir = git("rev-parse", "--git-dir")
    return Path(git_dir) / "restack-state.json"


def load_state() -> Optional[dict]:
    p = state_path()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def save_state(data: dict) -> None:
    state_path().write_text(json.dumps(data, indent=2) + "\n")


def delete_state() -> bool:
    p = state_path()
    if p.exists():
        p.unlink()
        return True
    return False


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> None:
    trunk = args.trunk or detect_trunk()
    branches = discover_branches(
        trunk,
        explicit=args.branches.split(",") if args.branches else None,
        prefix=args.prefix,
    )
    if not branches:
        print(f"trunk: {trunk}")
        print("\nno branches ahead of trunk")
        return

    status = compute_status(trunk, branches)
    if args.json:
        print(json.dumps(_to_dict(status), indent=2))
    else:
        print(format_compact_status(status))


def cmd_graph(args: argparse.Namespace) -> None:
    trunk = args.trunk or detect_trunk()
    branches = discover_branches(
        trunk,
        explicit=args.branches.split(",") if args.branches else None,
        prefix=args.prefix,
    )
    if not branches:
        print("no branches to graph")
        return

    graph = build_graph(trunk, branches)
    if args.json:
        print(json.dumps(_to_dict(graph), indent=2))
    else:
        print(format_compact_graph(graph))


def cmd_restack(args: argparse.Namespace) -> None:
    trunk = args.trunk or detect_trunk()
    branches = discover_branches(
        trunk,
        explicit=args.branches.split(",") if args.branches else None,
        prefix=args.prefix,
    )
    if not branches:
        print("no branches to restack")
        return

    graph = build_graph(trunk, branches)

    if graph.ambiguities:
        print("error: ambiguous graph, resolve before restacking", file=sys.stderr)
        print("", file=sys.stderr)
        print(format_compact_graph(graph), file=sys.stderr)
        sys.exit(1)

    # Determine which branches need restacking
    if args.branch:
        # Restack only descendants of the specified branch (not the branch itself).
        # This is the mid-stack edit case: the user already changed the branch,
        # so we cascade the change to its children.
        target = args.branch
        to_restack = _descendants_of(target, graph.parents, graph.order)
    else:
        # Restack everything that needs it
        to_restack = []
        for branch in graph.order:
            parent = graph.parents.get(branch, trunk)
            state = _branch_state(branch, parent, trunk)
            if state == "needs-restack":
                # Also include all descendants (they'll need restacking too)
                to_restack.append(branch)
                to_restack.extend(_descendants_of(branch, graph.parents, graph.order))
        # Deduplicate preserving topological order
        seen = set()
        deduped = []
        for b in to_restack:
            if b not in seen:
                seen.add(b)
                deduped.append(b)
        to_restack = [b for b in graph.order if b in seen]

    if not to_restack:
        print("all branches up to date, nothing to restack")
        return

    # Create backups
    backups = create_backups(to_restack)

    # Save state for recovery
    save_state({
        "trunk": trunk,
        "to_restack": to_restack,
        "completed": [],
        "backups": {b: git_rev(b) for b in to_restack},
        "parents": graph.parents,
    })

    # Output the plan with rebase strategy for each branch
    plan_lines = []
    plan_details = []
    for branch in to_restack:
        parent = graph.parents.get(branch, trunk)
        if parent == trunk or parent not in graph.parents:
            plan_lines.append(f"{branch} onto {parent}")
            plan_details.append({
                "branch": branch, "parent": parent, "strategy": "rebase",
            })
        elif args.branch and parent == args.branch:
            # Immediate child of an edited branch — use merge-base as cut point
            # because backup ref captures post-edit state (not pre-edit)
            mb = git_merge_base(parent, branch)
            plan_lines.append(f"{branch} onto {parent} (--onto merge-base {mb[:8] if mb else '?'})")
            plan_details.append({
                "branch": branch, "parent": parent,
                "strategy": "onto-merge-base", "merge_base": mb,
            })
        else:
            plan_lines.append(f"{branch} onto {parent} (--onto)")
            plan_details.append({
                "branch": branch, "parent": parent, "strategy": "onto-backup",
            })

    if args.json:
        print(json.dumps({
            "to_restack": to_restack,
            "plan": plan_details,
            "edited_branch": args.branch,
        }))
    else:
        if args.branch:
            print(f"edited branch: {args.branch}")
        print(f"branches to restack: {','.join(to_restack)}")
        for line in plan_lines:
            print(f"  rebase: {line}")
        print(f"\nbackups created: {','.join(backups.values())}")


def cmd_sync(args: argparse.Namespace) -> None:
    trunk = args.trunk or detect_trunk()
    remote = args.remote or "origin"
    branches = discover_branches(
        trunk,
        explicit=args.branches.split(",") if args.branches else None,
        prefix=args.prefix,
    )

    # Report what we found
    landed = detect_landed(trunk, branches) if branches else []
    remaining = [b for b in branches if b not in landed]

    graph = build_graph(trunk, remaining) if remaining else None

    result = {
        "trunk": trunk,
        "remote": remote,
        "trunk_behind": git_count(f"{trunk}..{remote}/{trunk}") if git_test("rev-parse", "--verify", f"{remote}/{trunk}") else 0,
        "landed": landed,
        "remaining": remaining,
    }

    if graph:
        needs_restack = []
        for branch in graph.order:
            parent = graph.parents.get(branch, trunk)
            state = _branch_state(branch, parent, trunk)
            if state == "needs-restack":
                needs_restack.append(branch)
        result["needs_restack"] = needs_restack
        result["graph"] = _to_dict(graph)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        behind = result["trunk_behind"]
        print(f"trunk: {trunk} ({behind} behind {remote})" if behind else f"trunk: {trunk} (up to date)")
        print(f"landed: {','.join(landed) or '(none)'}")
        print(f"remaining: {','.join(remaining) or '(none)'}")
        if result.get("needs_restack"):
            print(f"needs-restack: {','.join(result['needs_restack'])}")
        if graph and graph.ambiguities:
            for amb in graph.ambiguities:
                branch_strs = [
                    f"{d['branch']}({d['commits']} commits)"
                    for d in amb.details
                ]
                print(f"ambiguous: {','.join(branch_strs)} fork from {amb.fork_point}")


def cmd_cleanup(args: argparse.Namespace) -> None:
    deleted = delete_backups()
    state_existed = delete_state()

    if args.json:
        print(json.dumps({"deleted_backups": deleted, "state_deleted": state_existed}))
    else:
        if deleted:
            print(f"deleted backups: {','.join(deleted)}")
        else:
            print("no backups to delete")
        if state_existed:
            print("state file deleted")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _descendants_of(
    branch: str,
    parents: Dict[str, str],
    order: List[str],
) -> List[str]:
    """Find all descendants of a branch in topological order."""
    descendants = set()
    queue = [branch]
    while queue:
        current = queue.pop(0)
        for b, p in parents.items():
            if p == current and b not in descendants:
                descendants.add(b)
                queue.append(b)
    return [b for b in order if b in descendants]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="restack",
        description="Stacked branch management utilities for Claude.",
    )
    parser.add_argument("--trunk", help="Trunk branch (default: auto-detect main/master)")
    parser.add_argument("--branches", help="Comma-separated list of branches to analyze")
    parser.add_argument("--prefix", help="Branch prefix filter (e.g. 'paul/')")
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of compact format",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "status",
        help="Show inferred stacks with branch states",
    )

    subparsers.add_parser(
        "graph",
        help="Output inferred dependency graph",
    )

    restack_parser = subparsers.add_parser(
        "restack",
        help="Plan and prepare cascading rebases",
    )
    restack_parser.add_argument(
        "--branch",
        help="Restack only this branch and its descendants",
    )

    sync_parser = subparsers.add_parser(
        "sync",
        help="Analyze trunk state, detect landed branches, find what needs restacking",
    )
    sync_parser.add_argument(
        "--remote", default="origin",
        help="Remote to sync with (default: origin)",
    )

    subparsers.add_parser(
        "cleanup",
        help="Delete backup refs and state file",
    )

    args = parser.parse_args()

    dispatch = {
        "status": cmd_status,
        "graph": cmd_graph,
        "restack": cmd_restack,
        "sync": cmd_sync,
        "cleanup": cmd_cleanup,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
