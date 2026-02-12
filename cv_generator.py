#!/usr/bin/env python3
"""Compatibility wrapper for the modular CV Generator CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_DIRECTORY = PROJECT_ROOT / "src"

if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from cli import main


if __name__ == "__main__":
    raise SystemExit(main())
