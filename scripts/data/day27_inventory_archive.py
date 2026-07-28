from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import json
from data.day27.hashing import sha256_file
from data.day27.safe_archive import inventory_archive

parser = argparse.ArgumentParser()
parser.add_argument("--archive", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
report = inventory_archive(args.archive)
report["archivePath"] = str(args.archive)
report["archiveSha256"] = sha256_file(args.archive)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(args.output)
raise SystemExit(0 if report["safeToExtract"] else 2)
