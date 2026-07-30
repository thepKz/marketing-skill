#!/usr/bin/env python3
"""Shared .env loader.

Image generation is optional and provider-specific, so its base URL, key, and model
live outside version control. This reads `.env` from the repository root and sets
values into `os.environ` only where a variable is not already set, so a real shell
export always wins over the file. Values are never printed or logged by this module;
callers must keep the same discipline.
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def _find_env_file() -> Path | None:
    candidate = SKILL_ROOT
    for _ in range(4):
        env_file = candidate / ".env"
        if env_file.exists():
            return env_file
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    return None


def load_env(path: Path | None = None) -> None:
    target = path or _find_env_file()
    if target is None or not target.exists():
        return
    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get(name: str, default: str = "") -> str:
    load_env()
    return os.environ.get(name, default)
