from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import json
from data.day27.profile_driven_csv_adapter import convert_wide_csv_smoke

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--profile", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
profile = json.loads(args.profile.read_text(encoding="utf-8"))
result = convert_wide_csv_smoke(args.input, profile, args.output_dir)
print(json.dumps({"status":"PASS","npz":str(result.npz_path),"sidecar":str(result.sidecar_path),"sampleCount":result.sample_count,"channelCount":result.channel_count}, ensure_ascii=False, indent=2))
