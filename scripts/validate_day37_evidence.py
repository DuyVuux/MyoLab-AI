import sys
import json
from pathlib import Path

def validate(evidence_path: str):
    path = Path(evidence_path)
    if not path.exists():
        print(f"File not found: {evidence_path}")
        sys.exit(1)
        
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
        
    required_keys = ["schema_version", "repeatability", "similarity", "sealed_test_rows_read", "pooled_dataset", "hard_fatigue_diagnosis_allowed"]
    for key in required_keys:
        if key not in data:
            print(f"Missing required key in evidence: {key}")
            sys.exit(1)
            
    if data["sealed_test_rows_read"] != 0:
        print("ERROR: Sealed test was opened!")
        sys.exit(1)
        
    if data["pooled_dataset"] is not False:
        print("ERROR: Pooled dataset detected!")
        sys.exit(1)
        
    if data["hard_fatigue_diagnosis_allowed"] is not False:
        print("ERROR: Hard fatigue diagnosis must not be allowed.")
        sys.exit(1)
        
    print("Evidence validation passed.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_day37_evidence.py <path_to_json>")
        sys.exit(1)
    validate(sys.argv[1])
