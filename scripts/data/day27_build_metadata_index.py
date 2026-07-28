from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import csv
import json
import re

from data.day27.hashing import sha256_file
from data.day27.label_mapping import map_label, validate_label_map

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--profile", type=Path, required=True)
parser.add_argument("--label-map", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
profile = json.loads(args.profile.read_text(encoding="utf-8"))
label_config = json.loads(args.label_map.read_text(encoding="utf-8"))
mapping = validate_label_map(label_config)
if profile.get("verificationStatus") != "VERIFIED":
    raise SystemExit("PROFILE_NOT_VERIFIED")
regex = re.compile(profile["pathMetadata"]["regex"])
rows = []
for path in sorted(args.root.glob(profile["fileGlob"])):
    if not path.is_file():
        continue
    rel = str(path.relative_to(args.root)).replace("\\", "/")
    match = regex.fullmatch(rel) or regex.search(rel)
    if not match:
        raise SystemExit(f"PATH_METADATA_REGEX_MISMATCH:{rel}")
    groups = match.groupdict()
    target = map_label(groups["source_label"], mapping)
    rows.append({
        "source_path": rel,
        "source_sha256": sha256_file(path),
        "subject_id": groups["subject_id"],
        "day_id": groups.get("day_id") or "",
        "session_id": groups.get("session_id") or "",
        "trial_id": groups.get("trial_id") or "",
        "repetition_id": groups["repetition_id"],
        "source_label": groups["source_label"],
        "canonical_label": target,
        "sampling_rate_hz": profile["signal"]["samplingRateHz"],
        "channel_count": len(profile["signal"]["channels"]),
        "signal_unit": profile["signal"]["sourceUnit"],
    })
if not rows:
    raise SystemExit("NO_FILES_MATCHED")
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
print(args.output)
