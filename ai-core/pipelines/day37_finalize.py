import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-gate", required=True)
    parser.add_argument("--synthetic-evidence", required=True)
    parser.add_argument("--integration-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    input_gate = json.loads(Path(args.input_gate).read_text(encoding="utf-8"))
    
    if not input_gate.get("day36_status_accepted") or input_gate.get("hard_fatigue_diagnosis_allowed"):
        print("Day 36 Input Gate failed. Blocking Day 37.")
        status = "BLOCKED_WITH_EVIDENCE"
    else:
        status = "GO_FOR_DAY38_TASK_C_VALIDATION"
        
    manifest = {
        "status": status,
        "input_gate_verified": True,
        "synthetic_evidence_processed": Path(args.synthetic_evidence).exists(),
        "sealed_test_opened": False,
        "clinical_use_allowed": False,
        "production_promotion_allowed": False
    }
    
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    print(f"Final manifest written to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
