"""Test-path bootstrap for the monorepo Day 3 layout."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "packages" / "semg-core",
    ROOT / "services" / "signal-ingestion-service" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
