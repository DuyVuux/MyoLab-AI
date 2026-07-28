from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import csv
import json
from data.day27.group_split import build_subject_split

parser = argparse.ArgumentParser()
parser.add_argument("--metadata-index", type=Path, required=True)
parser.add_argument("--dataset-id", required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--seed", type=int, default=2701)
args = parser.parse_args()
with args.metadata_index.open("r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
report = build_subject_split(rows, dataset_id=args.dataset_id, seed=args.seed)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(args.output)
