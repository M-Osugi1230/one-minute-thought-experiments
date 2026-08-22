#!/usr/bin/env python3
"""Repository-local entry point.

This wrapper keeps `python pipeline.py ...` working without requiring an
editable package install first.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from thought_pipeline.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
