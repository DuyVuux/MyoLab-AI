#!/usr/bin/env python3
"""Ghi environment DSP không chứa secret/PHI."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    buffer = StringIO()
    with redirect_stdout(buffer):
        np.__config__.show()
    payload = {
        "schema_version": "dsp-environment.v0.1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "architecture": platform.architecture()[0],
            "byteorder": sys.byteorder,
        },
        "libraries": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pyyaml": yaml.__version__,
        },
        "numpy_build_configuration": buffer.getvalue(),
        "privacy_note": "Không lưu username, home directory, secret hoặc PHI.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output), "libraries": payload["libraries"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
