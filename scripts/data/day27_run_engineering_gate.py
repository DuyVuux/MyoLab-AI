from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import json
from data.day27.engineering_gate import build_engineering_gate

parser = argparse.ArgumentParser()
parser.add_argument("--gate-input", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
inputs = json.loads(args.gate_input.read_text(encoding="utf-8"))
report = build_engineering_gate(inputs)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(args.output)
raise SystemExit(0 if report["status"] == "GO_FOR_DAY28_EDA" else 2)
