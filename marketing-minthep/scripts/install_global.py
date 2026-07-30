#!/usr/bin/env python3
"""Install the canonical skill into the global Claude and Codex skill directories.

Both agents load skills from a per-user directory, not from this repository, so a global
install is a copy. Copies go stale silently — the previous one sat a week behind the repo
while still answering requests — so this script mirrors rather than merges: it deletes the
destination first, then copies, so a file removed here disappears there too.

The repo-local adapters under `.claude/` and `.codex/` point at the canonical skill with a
relative path, which only resolves from inside the repo. The global copy is the whole skill,
so no adapter and no path rewriting is needed.

    python marketing-minthep/scripts/install_global.py            # install
    python marketing-minthep/scripts/install_global.py --check    # report drift, change nothing
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = SKILL_ROOT.name

# Caches and scratch must never reach a global install: they are large, machine-specific, and
# would be read as skill content by an agent that does not know better.
# agents.zip is a 1 MB build artifact of the repo, not skill content. Shipping it made every
# install a megabyte heavier for a file no agent reads.
EXCLUDE = shutil.ignore_patterns("__pycache__", "*.pyc", ".tmp*", "undefined", ".impeccable", "*.zip")
# Names EXCLUDE drops, so --check does not report them as drift the install failed to fix.
IGNORED = {"__pycache__", ".impeccable", "undefined", "agents.zip"}


def targets() -> list[Path]:
    home = Path.home()
    return [home / ".claude" / "skills" / SKILL_NAME, home / ".codex" / "skills" / SKILL_NAME]


def drift(source: Path, destination: Path) -> list[str]:
    """Report paths that differ, so --check can be honest about what an install would change."""
    if not destination.exists():
        return ["<not installed>"]
    differences: list[str] = []
    comparison = filecmp.dircmp(source, destination, ignore=sorted(IGNORED))

    def walk(node: filecmp.dircmp, prefix: str) -> None:
        for name in node.left_only:
            differences.append(f"+ {prefix}{name}")
        for name in node.right_only:
            differences.append(f"- {prefix}{name}")
        for name in node.diff_files:
            differences.append(f"~ {prefix}{name}")
        for name, child in node.subdirs.items():
            walk(child, f"{prefix}{name}/")

    walk(comparison, "")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    arguments = parser.parse_args()

    exit_code = 0
    for destination in targets():
        differences = drift(SKILL_ROOT, destination)
        label = destination.parent.parent.name  # .claude or .codex

        if arguments.check:
            if differences:
                exit_code = 1
                print(f"{label}: {len(differences)} differences")
                for line in differences[:12]:
                    print(f"  {line}")
                if len(differences) > 12:
                    print(f"  ... and {len(differences) - 12} more")
            else:
                print(f"{label}: up to date")
            continue

        if not differences:
            print(f"{label}: already up to date")
            continue

        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL_ROOT, destination, ignore=EXCLUDE)

        remaining = drift(SKILL_ROOT, destination)
        # Only the exclusions may legitimately be missing after a copy.
        unexpected = [line for line in remaining if not line.startswith("+ ")]
        if unexpected:
            print(f"{label}: install left unexpected differences: {unexpected[:5]}")
            exit_code = 1
        else:
            files = sum(1 for path in destination.rglob("*") if path.is_file())
            print(f"{label}: installed {files} files -> {destination}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
