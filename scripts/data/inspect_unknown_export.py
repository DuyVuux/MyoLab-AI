#!/usr/bin/env python3
"""Inspect an unknown export bundle and produce a structured inventory.

This tool does not need to know the vendor beforehand. When actual export
files arrive from Motion Lab (or any other source), it generates an initial
inventory to guide adapter construction.

Usage:
    python3 scripts/data/inspect_unknown_export.py \
        --input path/to/export/bundle \
        --output qa-validation/evidence/site-export-inspection.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional heavy imports — degrade gracefully
# ---------------------------------------------------------------------------
try:
    import scipy.io as sio  # type: ignore
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import ezc3d  # type: ignore
    HAS_EZC3D = True
except ImportError:
    HAS_EZC3D = False


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def _detect_encoding(raw: bytes) -> list[str]:
    """Return candidate encodings (simple heuristic)."""
    candidates: list[str] = []
    for enc in ("utf-8", "latin-1", "cp1252", "ascii"):
        try:
            raw.decode(enc)
            candidates.append(enc)
        except (UnicodeDecodeError, ValueError):
            pass
    return candidates


def _detect_delimiter(text: str) -> list[str]:
    """Guess CSV delimiter from first 8 KB."""
    sample = text[:8192]
    counts = {d: sample.count(d) for d in [",", "\t", ";", "|"]}
    return [d for d, c in sorted(counts.items(), key=lambda x: -x[1]) if c > 0]


TIME_HINTS = {"time", "t", "timestamp", "sample", "frame", "index", "elapsed"}
SIGNAL_HINTS = {"emg", "signal", "ch", "channel", "sensor", "analog", "mv", "uv"}


def _classify_headers(headers: list[str]) -> tuple[list[str], list[str]]:
    time_cols: list[str] = []
    signal_cols: list[str] = []
    for h in headers:
        low = h.lower().strip()
        if any(hint in low for hint in TIME_HINTS):
            time_cols.append(h)
        if any(hint in low for hint in SIGNAL_HINTS):
            signal_cols.append(h)
    return time_cols, signal_cols


def inspect(input_path: Path) -> dict:
    """Build an inspection report for *input_path* (file or directory)."""
    report: dict = {
        "inspectionVersion": "0.1.0",
        "inspectedAt": datetime.now(timezone.utc).isoformat(),
        "inputPath": str(input_path),
        "inputHashSha256": None,
        "fileTree": [],
        "extensions": [],
        "fileSizes": {},
        "encodingCandidates": [],
        "delimiterCandidates": [],
        "csvHeaders": [],
        "sheetNames": [],
        "matVariables": [],
        "c3dAnalogChannels": [],
        "candidateTimeColumns": [],
        "candidateSignalColumns": [],
    }

    if input_path.is_file():
        files = [input_path]
        base = input_path.parent
        report["inputHashSha256"] = _sha256(input_path)
    else:
        files = sorted(input_path.rglob("*"))
        base = input_path

    ext_set: set[str] = set()
    all_time: list[str] = []
    all_signal: list[str] = []
    all_encodings: set[str] = set()
    all_delimiters: set[str] = set()

    for fp in files:
        if not fp.is_file():
            continue
        rel = str(fp.relative_to(base))
        ext = fp.suffix.lower()
        sz = fp.stat().st_size
        ext_set.add(ext)
        report["fileTree"].append({
            "relativePath": rel,
            "sizeBytes": sz,
            "extension": ext,
            "mimeType": None,
        })
        report["fileSizes"][rel] = sz

        # --- CSV / text ---
        if ext in {".csv", ".txt", ".tsv", ".asc", ".ascii", ".dat"}:
            try:
                raw = fp.read_bytes()[:1 << 20]  # first 1 MB
                encs = _detect_encoding(raw)
                all_encodings.update(encs)
                text = raw.decode(encs[0] if encs else "latin-1", errors="replace")
                delims = _detect_delimiter(text)
                all_delimiters.update(delims)
                reader = csv.reader(io.StringIO(text), delimiter=delims[0] if delims else ",")
                rows = list(reader)
                headers = rows[0] if rows else []
                tc, sc = _classify_headers(headers)
                all_time.extend(tc)
                all_signal.extend(sc)
                report["csvHeaders"].append({
                    "file": rel,
                    "headers": headers,
                    "rowCount": len(rows),
                    "columnCount": len(headers),
                })
            except Exception:
                pass

        # --- MATLAB ---
        if ext in {".mat"} and HAS_SCIPY:
            try:
                mat = sio.loadmat(str(fp), squeeze_me=False)
                variables = [k for k in mat if not k.startswith("__")]
                report["matVariables"].append({
                    "file": rel,
                    "variables": variables,
                })
            except Exception:
                pass

        # --- C3D ---
        if ext in {".c3d"} and HAS_EZC3D:
            try:
                c = ezc3d.c3d(str(fp))
                labels = list(c["parameters"]["ANALOG"]["LABELS"]["value"])
                report["c3dAnalogChannels"].append({
                    "file": rel,
                    "channels": labels,
                })
            except Exception:
                pass

    report["extensions"] = sorted(ext_set)
    report["encodingCandidates"] = sorted(all_encodings)
    report["delimiterCandidates"] = sorted(all_delimiters)
    report["candidateTimeColumns"] = sorted(set(all_time))
    report["candidateSignalColumns"] = sorted(set(all_signal))

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect an unknown export bundle."
    )
    parser.add_argument("--input", required=True, help="Path to file or directory")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"Input not found: {inp}", file=sys.stderr)
        raise SystemExit(1)

    report = inspect(inp)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Inspection report written to {out}")
    print(f"  files: {len(report['fileTree'])}")
    print(f"  extensions: {report['extensions']}")
    print(f"  candidate time columns: {report['candidateTimeColumns']}")
    print(f"  candidate signal columns: {report['candidateSignalColumns']}")


if __name__ == "__main__":
    main()
