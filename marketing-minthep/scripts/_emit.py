#!/usr/bin/env python3
"""Shared output helper.

Every script in this skill can emit Vietnamese. On Windows, stdout defaults to cp1252 and
any diacritic raises UnicodeEncodeError, so stdout is reconfigured to UTF-8 before writing.
Files are always written UTF-8 without a BOM so downstream tools read them consistently.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def use_utf8_stdout() -> None:
    """Force UTF-8 on stdout and stderr where the runtime allows it."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def emit(content: str, output: str | Path | None = None) -> None:
    """Write to a file when asked, otherwise print. Always UTF-8."""
    use_utf8_stdout()
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def emit_json(payload: object, output: str | Path | None = None) -> None:
    emit(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", output)


def run_gate(main) -> None:
    """Exit-code discipline for gate scripts.

    0 clean, 2 fail, 3 unsettled are verdicts about the artifact. A gate that cannot run —
    input missing, unreadable, undecodable — has no verdict and must not look like one, so
    that failure exits 4 and says so. A crash scored as a defect (or as a pass) steers the
    run on evidence that does not exist.
    """
    use_utf8_stdout()
    try:
        sys.exit(main())
    except (OSError, UnicodeDecodeError) as exc:
        print(f"verdict: no-verdict (gate could not run: {exc})", file=sys.stderr)
        sys.exit(4)
