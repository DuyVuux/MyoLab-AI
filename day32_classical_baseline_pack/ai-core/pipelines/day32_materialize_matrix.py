from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import argparse, json
import numpy as np
from day32.matrix_gate import validate_matrix

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-npz", required=True)
    p.add_argument("--dataset-view", required=True)
    p.add_argument("--feature-arm", required=True)
    p.add_argument("--output-manifest", required=True)
    args = p.parse_args()
    data = np.load(args.input_npz, allow_pickle=False)
    result = validate_matrix(
        data["X"], data["y"], data["groups"], data["dataset_ids"],
        args.dataset_view, args.feature_arm,
    )
    out = Path(args.output_manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
