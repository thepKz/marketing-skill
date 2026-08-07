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

from _emit import use_utf8_stdout
import filecmp
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = SKILL_ROOT.name

# What must never reach a global install. One rule covers every entry: if the repository will not
# commit it, an install will not copy it. `.gitignore` is the other half of that rule, and a test
# binds the two together, because they had already drifted apart once - `research_assets/` was
# ignored here and shipped there, so the next install would have put 25 MB of cached vendor help
# pages into two directories where an agent reads everything it finds as skill content.
NEVER_INSTALL = (
    # Interpreter and build artifacts. agents.zip is a 1 MB bundle of the agent definitions,
    # rebuilt on demand; shipping it made every install a megabyte heavier for a file no agent reads.
    "__pycache__", "*.pyc", "*.zip",
    # Anything hidden. A dot-prefixed entry inside the skill is state some tool wrote next to its
    # working directory, and no skill content is ever hidden - SKILL.md, references, data, scripts
    # and assets are all things a reader is meant to open. Stated as a rule rather than as a list of
    # tool names, because the skill should not have to know which tools the author happens to run.
    ".*",
    # Credentials, and the sharpest entry on the list. scripts/generate_image.py reads a bearer
    # token through scripts/_env.py, which looks for a .env beside the skill. Copying one would put
    # a live key in two directories outside the repository, where no .gitignore is watching it.
    # Overlaps the hidden rule above on purpose: if that rule is ever narrowed, keys stay out.
    ".env", ".env.*", "*.key", "_secrets",
    # Scratch from research subagents: fetched HTML, arithmetic checks, half-finished sweeps.
    ".tmp*", "undefined", "_research", "_work",
    # Somebody else's property, cached to verify a claim: gazette pages behind the legal tables,
    # vendor help-centre pages behind the platform defaults, photographs behind the colour
    # calibration. Local reading is the point. Two copies on disk outside the repo is not.
    "research_assets",
    # Per-project output, not skill content. The stale runs/ directory still sitting in the Codex
    # install is what this line is for.
    "runs",
)
EXCLUDE = shutil.ignore_patterns(*NEVER_INSTALL)


def targets() -> list[Path]:
    home = Path.home()
    return [home / ".claude" / "skills" / SKILL_NAME, home / ".codex" / "skills" / SKILL_NAME]


def excluded_names(root: Path) -> list[str]:
    """Every name under `root` that EXCLUDE drops, so --check does not report an exclusion as drift
    the install failed to fix.

    Derived rather than listed, because the hand-written version of this list was missing three of
    the names EXCLUDE already dropped, and `--check` reported them as differences forever. The walk
    prunes: nothing descends into a directory that is itself excluded, which is what keeps a 100 MB
    gazette cache from being enumerated file by file to learn something already known at its root.

    Flat basenames, because that is what `filecmp.dircmp` takes and it inherits them into subdirs.
    Good enough here - every name on the list is scratch or cache, and none of them is also a
    legitimate name for skill content at some other depth.
    """
    names: set[str] = set()
    stack = [root]
    while stack:
        current = stack.pop()
        entries = sorted(path.name for path in current.iterdir())
        dropped = EXCLUDE(str(current), entries)
        names |= dropped
        stack.extend(path for path in current.iterdir()
                     if path.is_dir() and path.name not in dropped)
    return sorted(names)


def drift(source: Path, destination: Path) -> list[str]:
    """Report paths that differ, so --check can be honest about what an install would change."""
    if not destination.exists():
        return ["<not installed>"]
    differences: list[str] = []
    comparison = filecmp.dircmp(source, destination, ignore=excluded_names(source))

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
    use_utf8_stdout()
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
