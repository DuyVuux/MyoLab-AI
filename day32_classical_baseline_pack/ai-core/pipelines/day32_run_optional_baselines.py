from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import argparse, json
from day32.model_factory import OPTIONAL_MODEL_IDS

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--core-gate", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    gate = json.loads(Path(args.core_gate).read_text(encoding="utf-8"))
    status = gate.get("core_gate", gate).get("status")
    if status not in {"CORE_GATE_PASS", "CORE_GATE_PASS_WITH_MODEL_FAILURES"}:
        raise PermissionError("Optional models require core gate")
    result = {
        "schema_version": "day32-optional-plan.v1",
        "status": "ELIGIBLE_FOR_CONTROLLED_EXECUTION",
        "models": list(OPTIONAL_MODEL_IDS),
        "real_fitting_executed": False,
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
