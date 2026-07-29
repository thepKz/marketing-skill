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
