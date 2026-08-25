#!/usr/bin/env python3
import json,sys
from pathlib import Path
def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    p=root/"qa-validation/evidence/ui-i4-live-backend-binding.json"
    if not p.exists():
        print("BLOCKED_UI_I4_BINDING: missing",p); return 5
    d=json.loads(p.read_text());e=[]
    if d.get("status")!="PASS":e.append("status != PASS")
    b=d.get("canonical_bindings") or {}
    for k in ["session_read_model","pipeline_job_read_model","qc_read_model","review_queue_read_model"]:
        if not b.get(k):e.append("missing binding: "+k)
    s=d.get("real_mode_smoke") or {}
    if s.get("mock_or_demo_backend_used") is not False:e.append("mock/demo backend must be false")
    for k in ["executed","operations_summary_observed","source_is_canonical_read_model","counts_non_negative"]:
        if s.get(k) is not True:e.append("smoke false: "+k)
    if e:
        print("BLOCKED_UI_I4_BINDING");[print("-",x) for x in e];return 5
    print("PASS: UI-I4 live operations binding")
    return 0
if __name__=="__main__": raise SystemExit(main())
