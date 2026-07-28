from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import json
from data.day27.source_record import validate_source_record

parser = argparse.ArgumentParser()
parser.add_argument("--record", type=Path, required=True)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
record = json.loads(args.record.read_text(encoding="utf-8"))
report = validate_source_record(record)
text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
print(text, end="")
raise SystemExit(0 if report["status"] == "VERIFIED" else 2)
